import os
from sentence_transformers import SentenceTransformer
import sys
import torch
import pickle
import numpy

sentence_path = sys.argv[1]
sent_cache_path = sentence_path + '.pickle'
emb_cache_path = sentence_path + '.emb.pickle'
index_path = sentence_path + '.emb.index'
modelname = 'all-MiniLM-L6-v2'
device = torch.device("cuda")


if os.path.exists(sent_cache_path):
    with open(sent_cache_path, "rb") as f:
        sentences = pickle.load(f)
else:
    with open(sentence_path) as f:
        sentences = f.read().splitlines()

    with open(sent_cache_path, "wb") as f:
        pickle.dump(sentences, f, protocol=pickle.HIGHEST_PROTOCOL)

if os.path.exists(emb_cache_path):
    with open(emb_cache_path, "rb") as f:
        embeddings = pickle.load(f)
else:
    model = SentenceTransformer(modelname)
    model.max_seq_length = 256
    model = model.to(device)
    embeddings = model.encode(sentences, show_progress_bar=True, batch_size=512, convert_to_tensor=True)
    torch.nn.functional.normalize(embeddings, out=embeddings)
    embeddings = embeddings.cpu().numpy()
    with open(emb_cache_path, "wb") as f:
        pickle.dump(embeddings, f, protocol=pickle.HIGHEST_PROTOCOL)

if not os.path.exists(index_path):
    import hnswlib
    index = hnswlib.Index(space = 'ip', dim = embeddings.shape[1])
    index.init_index(max_elements = len(embeddings), ef_construction = 400, M = 64)
    index.add_items(embeddings, numpy.arange(len(embeddings)))
    index.save_index(index_path)
    print('Saved index with dimensions', embeddings.shape[1], 'to file:', index_path)
