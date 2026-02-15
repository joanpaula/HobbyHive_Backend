from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv()

secret_key = os.getenv("JWT_SECRET")

mongo_uri = os.getenv("MONGO_URI")

uri = os.getenv("MONGO_URI")
client = MongoClient(uri, server_api=ServerApi('1'))

aws_access_key = os.getenv("AWS_ACCESS_KEY")
aws_secret_key = os.getenv("AWS_SECRET_KEY")
aws_s3_bucket_name = os.getenv("AWS_S3_BUCKET_NAME")
aws_region = os.getenv("AWS_REGION")

db = client["hobbyhive"]