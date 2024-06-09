
from pymongo import MongoClient

client = MongoClient("mongodb+srv://Bhavana:Bhavana12@codegene.usxjnqx.mongodb.net/?retryWrites=true&w=majority&appName=codegene")
db = client["users"]
collection = db["user"]
history=db["transaction"]
# limit=db["limits"]
# if "history" not in db.list_collection_names():
#     validator= {
#         "$jsonSchema": {
#         "bsonType": "object",
#         "required": [
#             "transaction_id",
#             "user_id",
#             "amount",
#             "type",
#             "name",
#             "payment_category"
#         ],
#         "properties": {
#             "transaction_id": {
#             "bsonType": "string",
#             "description": "must be a string and is required"
#             },
#             "user_id": {
#             "bsonType": "string",
#             "description": "must be a string and is required"
#             },
#             "amount": {
#             "bsonType": "int",
#             "description": "must be an integer and is required"
#             },
#             "type": {
#             "bsonType": "string",
#             "description": "must be a string and is required"
#             },
#             "name": {
#             "bsonType": "string",
#             "description": "must be a string and is required"
#             },
#             "payment_mode": {
#             "bsonType": ["string", "null"],
#             "description": "must be a string"
#             },
#             "payment_status": {
#             "bsonType": ["string", "null"],
#             "description": "must be a string"
#             },
#             "payment_category": {
#             "bsonType": "string",
#             "description": "must be a string and is required"
#             },
#             # "transaction_date": {
#             # "bsonType": ["date", "null"],
#             # "description": "must be a date"
#             # }
#         }
#         }
#     }


#     db.create_collection("history",validator=validator)