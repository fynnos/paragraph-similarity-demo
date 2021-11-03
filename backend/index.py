from sentence_transformers import SentenceTransformer
import pickle
import hnswlib
import torch
import numpy

class SimilarSentenceIndex():
    def __init__(self, sent_path, index_path, emb_dim=384, model_name='all-MiniLM-L6-v2', max_seq_length=256):
        with open(sent_path, "rb") as f:
            self.sentences = pickle.load(f)
        self.index = hnswlib.Index(space = 'ip', dim = emb_dim)
        self.index.load_index(index_path)
        self.model = SentenceTransformer(model_name)
        self.model.max_seq_length = max_seq_length
    
    def query(self, sentence, topk=10):
        emb = self.model.encode(sentence, convert_to_tensor=True).unsqueeze(0)
        torch.nn.functional.normalize(emb, out=emb)
        inp_embedding = emb.squeeze(0).cpu().numpy()
        corpus_ids, distances = self.index.knn_query(inp_embedding, k=topk)
        sentences = [self.sentences[id] for id in corpus_ids[0]]
        return sentences, distances[0]
