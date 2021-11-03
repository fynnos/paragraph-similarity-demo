from flask import Flask, redirect
from flask import request
from flask import jsonify
from flask_cors import CORS
from index import SimilarSentenceIndex
import os

app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
CORS(app)

ssi = SimilarSentenceIndex(os.environ.get("SENTENCES"), os.environ.get("INDEX"))

@app.route('/', methods=["GET"])
def home():
    return redirect("index.html")

@app.route("/search", methods=['GET','POST'])
def search():
    query = request.get_data(as_text=True)
    sentences, distances = ssi.query(query)
    return jsonify([{"text": s, "score":1-d, "id":i} for i, (s, d) in enumerate(zip(sentences, distances))])
