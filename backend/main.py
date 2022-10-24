from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, FileResponse, HTMLResponse
from pydantic import BaseModel
from docs2index import DocSentenceIndex
import os

# app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
# CORS(app)
app = FastAPI()

if os.environ.get("DEPLOYMENT", "DEV") == "DEV":
    from fastapi.middleware.cors import CORSMiddleware
    origins = ["*"]
    app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
else:
    from fastapi.staticfiles import StaticFiles
    app.mount("/static/", StaticFiles(directory="web/static"), name="static")

    @app.get("/", response_class=FileResponse)
    def read_index(request: Request):
        path = 'web/index.html' 
        return FileResponse(path)

modelname = os.environ.get("MODEL", 'T-Systems-onsite/cross-en-de-roberta-sentence-transformer')
dimensions = int(os.environ.get("DIMENSIONS", "768"))
input = os.environ.get("INPUT", "/home/fschroeder/research/freeNews/OneMillionPostsCorpus/output")
cache = os.environ.get("CACHE", "cache")
device = os.environ.get("DEVICE", None)
dsi = DocSentenceIndex(modelname, dimensions, docs_path = input, cache_basename=cache, device=device)

class Query(BaseModel):
    query: str



@app.post("/search")
def search(query: Query):
    sentences, distances, doc_ids, sent_ids = dsi.query(query.query)
    titles = [dsi.titles[i] for i in doc_ids]
    return [{"text": sent, "score":1-dist, "id":i, "title": title} for i, sent, dist, did, sid, title in zip(range(len(sentences)), sentences, distances, doc_ids, sent_ids, titles)]
