from fastapi import FastAPI, HTTPException, Depends
from routers.login_functions import get_current_user
from database import collection
from bullmq import Queue, Worker
import asyncio
from routers.redis_function import redis
import json
from datetime import datetime
from routers.registration import generate_transaction_id



concurrency_limit = 1
semaphore = asyncio.Semaphore(concurrency_limit)

async def process_transaction(job,token=None):
    try:
        data = job.data
        if not isinstance(data, dict):
            data = json.loads(data)
        if not isinstance(data, dict):
            raise ValueError("Data is not a dictionary")
        transaction_type = data.get("type")
        if not transaction_type:
            raise ValueError("Transaction type not found in data")
        if transaction_type != "transaction":
            raise ValueError(f"Invalid job type: {transaction_type}")

        send = collection.find_one({"user_id": data["sender"]})
        receive = collection.find_one({"user_id": data["receiver"]})
        if not send or not receive:
            raise HTTPException(status_code=404, detail="Sender or receiver not found")
        
        if send["balance"] < data["amount"]:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        
        collection.find_one_and_update({"user_id": send["user_id"]}, {"$inc": {"balance": -data["amount"]}})
        collection.find_one_and_update({"user_id": receive["user_id"]}, {"$inc": {"balance": data["amount"]}})

        transaction_record = {
            "transaction_id": generate_transaction_id(), 
            "amount": data["amount"],
            "timestamp": datetime.utcnow().isoformat(),
            "type": "debit" if send["user_id"] == data["sender"] else "credit",
            # "counterparty": data["receiver"] if send["user_id"] == data["sender"] else data["sender"]
        }

        # Update sender's transaction history
        collection.find_one_and_update(
            {"user_id": send["user_id"]},
            {"$push": {"transaction_history": transaction_record}}
        )
        
        # Update receiver's transaction history
        transaction_record["type"] = "credit"
        collection.find_one_and_update(
            {"user_id": receive["user_id"]},
            {"$push": {"transaction_history": transaction_record}}
        )
        
        print("Transaction processed successfully:", data)
    except Exception as e:
        print("Error processing transaction:", str(e))

worker = Worker("myQueue", process_transaction,{"connection":"redis://127.0.0.1:6379"})

