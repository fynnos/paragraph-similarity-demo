import os
from typing import List
from sentence_transformers import SentenceTransformer
import numpy
import hnswlib
import json
import gzip

class DocSentenceIndex():
    def __init__(self, modelname: str, dimensions: int, docs_path: str = None, cache_basename: str = None, device: str = None):
        self.model = SentenceTransformer(modelname, device=device)
        self.model.max_seq_length = 256
        self.titles, self.docs, self.paragraphs, self.sentids = self.cachedDocs(docs_path, cache_basename)
        self.index = self.cachedIndex(self.paragraphs, self.sentids, dimensions, cache_basename)

    def parseDocs(self, docs_path: str):
        docs = []
        sentences_id = []
        docs_paragraphs = []
        filenames = os.listdir(docs_path)
        titles = [name.split("_")[2] for name in filenames]
        for i, fname in enumerate(filenames):
            with open(os.path.join(docs_path, fname)) as f:
                doc_str = f.read()
            docs.append(doc_str)
            paragraphs = doc_str.split("\n\n")
            docs_paragraphs.append(paragraphs)
            sentences_id.extend(range(i*1000, i*1000 + len(paragraphs)))
        return titles, docs, docs_paragraphs, numpy.asarray(sentences_id, dtype=numpy.int64)

    def cachedDocs(self, docs_path: str, cache_basename):
        use_cache = cache_basename is not None
        if use_cache:
            docsJsonPath = cache_basename + ".json.gz"
            docsNpPath = cache_basename + ".npy"   
        if use_cache and os.path.exists(docsJsonPath) and os.path.exists(docsNpPath):
            with gzip.open(docsJsonPath, "rt") as f:
                data = json.load(f)
            ids = numpy.load(docsNpPath)
            return data["titles"], data["docs"], data["paragraphs"], ids
        else:
            titles, docs, paragraphs, ids = self.parseDocs(docs_path)
            if use_cache:
                with gzip.open(docsJsonPath, "wt") as f:
                    data = {"titles": titles, "docs": docs, "paragraphs": paragraphs}
                    json.dump(data, f)
                numpy.save(docsNpPath, ids)
            return titles, docs, paragraphs, ids

    def cachedIndex(self, paragraphs: List[List[str]], ids: numpy.ndarray, dimensions: int, cache_basename: str = None):
        index = hnswlib.Index(space = "ip", dim = dimensions)
        use_cache = cache_basename is not None
        if use_cache:
            embPath = cache_basename + ".emb.npy"
            indexPath = cache_basename + ".index"
        if use_cache and os.path.exists(indexPath):
            index.load_index(indexPath)
        else:
            if use_cache and os.path.exists(embPath):
                embeddings = numpy.load(embPath)
            else:
                sentences = [s for l in paragraphs for s in l]
                embeddings = self.model.encode(sentences, show_progress_bar=True, convert_to_tensor=True, normalize_embeddings=True)
                embeddings = embeddings.cpu().numpy()
                if use_cache:
                    numpy.save(embPath, embeddings)
            assert(index.dim == embeddings.shape[1])
            print("Dim: ", index.dim)
            index.init_index(max_elements = len(embeddings))
            index.add_items(embeddings, ids)
            if use_cache:
                index.save_index(indexPath)
        return index
    
    def query(self, sentence, topk=10):
        emb = self.model.encode(sentence, convert_to_tensor=True, normalize_embeddings=True)
        inp_embedding = emb.cpu().numpy()
        ids, distances = self.index.knn_query(inp_embedding, k=topk)
        ids = ids.astype(numpy.int64)
        doc_ids = (ids // 1000)[0].tolist()
        sent_ids = (ids % 1000)[0].tolist()
        sentences = [self.paragraphs[d][s] for d,s in zip(doc_ids, sent_ids)]
        return sentences, distances[0], doc_ids, sent_ids
    