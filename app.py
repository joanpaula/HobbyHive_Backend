import datetime
from bson import ObjectId
from bson import ObjectId
from flask import Flask, jsonify, make_response, request
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

try:
    client.admin.command("ping")
    print("MongoDB connected successfully")
except Exception as e:
    print("MongoDB connection failed:", e)

@app.route('/', methods=['GET'])
def index():
    return make_response("<h1>HobbyHive Backend is running!</h1>", 200)

@app.route('/posts', methods=['GET'])
def getPosts():
    posts = list(db.posts.find({}, {'_id': 0}))
    return make_response(jsonify(posts), 200)

@app.route('/posts/create', methods=['POST'])
def createPost():

    # required = ["username", "body_text"]
    required = ["body_text"]
    missing = [f for f in required if f not in request.form]

    if missing:
        return make_response( jsonify({"error":"Missing fields required: " + ", ".join(missing)} ), 400)
    
    new_post = {
        "user_id": str(ObjectId()),
        "username": request.form["username"],
        "body_text": request.form["body_text"],
        "media_url": request.form.getlist("media_url"),
        "image": request.form.get("image", None),
        "created_at": datetime.datetime.utcnow().isoformat() + 'Z'
    }

    new_post_id = db.posts.insert_one(new_post)
    return make_response(jsonify({"message": "Post created", "post_id": str(new_post_id.inserted_id)}), 201)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)