from fastapi import FastAPI, HTTPException
from database import collection
from bullmq import Queue, Worker
import asyncio
# from routers.redis_function import redis
import json
from datetime import datetime
from routers.registration import generate_transaction_id
from redis.asyncio import Redis

redis =Redis(
  host='redis-19175.c14.us-east-1-2.ec2.redns.redis-cloud.com',
  port=19175,
  password='SUgs1JXtonLW8gV35QmNCNSOfKDq00gt')

concurrency_limit = 1
semaphore = asyncio.Semaphore(concurrency_limit)

async def process_transaction(job, token=None):
    # # try:
        # print("job name -->",job.from_queue.name)
        # print('--->',[i for i in job])
        # print('dir-->',dir(job.name))
        # print('dir data-->',dir(job.data))
        # print("job details -->", dict(()
        data = job.data
        print("jobdata--->", data)
        if isinstance(data, str):
            data = json.loads(data)
        transaction_type = data.get('type')
        print(transaction_type)
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
    # except Exception as e:
    #     print("Error processing transaction:", str(e))

worker = Worker(name="myQueue", processor=process_transaction, opts={"connection":redis})