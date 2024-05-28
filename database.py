
from pymongo import MongoClient

client = MongoClient("mongodb+srv://Bhavana:Bhavana12@codegene.usxjnqx.mongodb.net/?retryWrites=true&w=majority&appName=codegene")
db = client["users"]
collection = db["user"]
