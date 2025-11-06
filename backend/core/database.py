from pymongo import MongoClient
from config.settings import MONGO_DETAILS

client = MongoClient(MONGO_DETAILS)
db = client.finance_assistant
