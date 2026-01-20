from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import json
import os

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))

db = client["hobbyhive"]

with open("dummy_posts.json") as f:
    posts = json.load(f)

if db.posts.count_documents({}) == 0:
    db.posts.insert_many(posts)
    print("Dummy posts inserted successfully!")   
else:
    print("Posts already exist, skipping...")