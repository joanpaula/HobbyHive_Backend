from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv()

secret_key = os.getenv("JWT_SECRET")

mongo_uri = os.getenv("MONGO_URI")

uri = os.getenv("MONGO_URI")
client = MongoClient(uri, server_api=ServerApi('1'))

db = client["hobbyhive"]