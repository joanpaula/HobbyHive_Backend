from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import json
import os

# seed hobbies into db

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))

db = client["hobbyhive"]

with open("hobbies.json") as f:
    hobbies = json.load(f)

if db.hobbies.count_documents({}) == 0:
    db.hobbies.insert_many(hobbies)
    print("Hobbies inserted successfully!")   
else:
    print("Hobbies already exist, skipping...")