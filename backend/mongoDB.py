from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()
url = os.getenv("MONGO_URL")
client = MongoClient(url)
db = client["assignment"]
ai_logging_collection = db['ai_descriptions_logging']