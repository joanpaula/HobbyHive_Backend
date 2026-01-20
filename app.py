from flask import Flask, jsonify, make_response
from flask_cors import CORS
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app)

load_dotenv()
uri = os.getenv("MONGO_URI")
client = MongoClient(uri, server_api=ServerApi('1'))

db = client["hobbyhive"]

@app.route('/', methods=['GET'])
def index():
    return make_response("<h1>HobbyHive Backend is running!</h1>", 200)

@app.route('/posts', methods=['GET'])
def getPosts():
    posts = list(db.posts.find({}, {'_id': 0}))
    return make_response(jsonify(posts), 200)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)