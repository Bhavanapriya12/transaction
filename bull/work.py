from fastapi import FastAPI, HTTPException
from database import collection
from bullmq import Queue, Worker
import asyncio
# from routers.redis_function import redis
import json
from datetime import datetime
from routers.registration import generate_transaction_id
from redis.asyncio import Redis
from database import history
# from helpers.tigerbalm import tige
# from routers.balance_limit import cash
# from validators.user_validator import CashLimit,cash_limit 
import logging
from datetime import datetime

logging.basicConfig(filename='transaction_logs.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_transaction(sender, receiver, amount, success=True):
    if success:
        logging.info(f"Transaction successful - Sender: {sender}, Receiver: {receiver}, Amount: {amount}")
    else:
        logging.error(f"Transaction failed - Sender: {sender}, Receiver: {receiver}, Amount: {amount}")


# error_logger = logger.error('error', logging.ERROR)
# info_logger = logger.info('info', logging.INFO)

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
    try:
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
        
        # cash(cash_limit,user_id=send["user_id"],amount=data["amount"],cash_type="debit")
        # cash(cash_limit,user_id=receive["user_id"],amount=data["amount"],cash_type="credit")
        collection.find_one_and_update({"user_id": send["user_id"]}, {"$inc": {"balance": -data["amount"]}})
        collection.find_one_and_update({"user_id": receive["user_id"]}, {"$inc": {"balance": data["amount"]}})

        send["cashout_daily_used"] += data["amount"]
        send["cashout_monthly_used"] += data["amount"]
        send["cashout_yearly_used"] += data["amount"]
        collection.update_one({"user_id": send["user_id"]}, {"$set": send})
        receive["cashin_daily_used"] += data["amount"]
        receive["cashin_monthly_used"] += data["amount"]
        receive["cashin_yearly_used"] += data["amount"]
        collection.update_one({"user_id": receive["user_id"]}, {"$set": receive})

        charges=0.01
        charge=data["amount"]*charges
        if send["user_id"] == data["sender"]:
            # formatted_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # phone_number=tige.decrypt(send["phone_number"])
            transaction_record={
                
                "transaction_id": generate_transaction_id(),
                "user_id": send["user_id"]  ,
                "amount": data["amount"],
                "charges":charge,
                "type": "debit" ,
                "name":send["username"],
                "receiver":receive["user_id"],
                "sender":send["user_id"],
                # "payment_mode":"online",
                # "payment_status":"success",
                "phone_number":send["phone_number"],
                "email":send["email"],
                "payment_category":data["payment_category"],
                "transaction_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            }

        history.insert_one(transaction_record)

             
        transaction={
            "transaction_id":transaction_record.get("transaction_id"),
            "user_id": receive["user_id"],
            "charges":charge,
            "amount": data["amount"],
            "type": "credit",
            "name":receive["username"],
            # "payment_mode":"online",
            # "payment_status":"success",
            "phone_number":receive["phone_number"],
            "email":receive["email"],
            "payment_category":data["payment_category"],
            "sender":send["user_id"],
            "receiver":receive["user_id"],
            "mode":"offline",
            "transaction_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        history.insert_one(transaction)
        log_transaction(send["user_id"],receive["user_id"],data["amount"])
        print("Transaction processed successfully:", data)
    except Exception as err:
        log_transaction(send["user_id"],receive["user_id"],data["amount"],success=False)
        raise err

worker = Worker(name="myQueue", processor=process_transaction, opts={"connection":redis})