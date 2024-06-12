from fastapi import FastAPI, HTTPException
from database import collection
from bullmq import Queue, Worker
import asyncio
# from routers.redis_function import redis
import os
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


# now = datetime.now()
# FOLDER = f"logs/{now.year}/{now.month}/{now.day}/{user_id}"
# folder_path = os.path.join(os.getcwd(), FOLDER)
# os.makedirs(folder_path, exist_ok=True)

# log_file_path = os.path.join(folder_path, 'transaction_logs.txt')
# logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
def setup_logging(user_id,date=datetime.now()):
    # date= datetime.now()

    FOLDER = f"logs/{date.year}/{date.month}/{date.day}/{user_id}"
    folder_path = os.path.join(os.getcwd(), FOLDER)

    os.makedirs(folder_path, exist_ok=True)

    log_file_path = os.path.join(folder_path, 'transaction_logs.txt')

    logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    return log_file_path

def read_log_file(log_file_path):
    if not os.path.exists(log_file_path):
        return []
    
    with open(log_file_path, 'r') as log_file:
        logs = log_file.readlines()
    
    return logs


# def log_transaction(sender, receiver, amount, success=True):
#     if success:
#         # setup_logging(sender)
#         # setup_logging(receiver)
#         logging.info(f"Transaction successful - Sender: {sender}, Receiver: {receiver}, Amount: {amount}")
#     else:
#         # setup_logging(sender)
#         # setup_logging(receiver)

#         logging.error(f"Transaction failed - Sender: {sender}, Receiver: {receiver}, Amount: {amount}")
def log_transaction(user_id,balance,amount,router):
    # before_balance = balance['before_balance']
    # after_balance = balance['after_balance']
    success=True
    
    log_path = setup_logging(user_id)
    log_message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - "
    log_message += "INFO - " if success else "ERROR - "
    log_message += f"Transaction {'successful' if success else 'failed'}, amount={amount}, "
    log_message += f"balance: {balance}, "
    log_message +=f"route:{router}\n"

    with open(log_path, 'a') as log_file:
        log_file.write(log_message)
    
    # receiver = collection.find_one({"user_id": receiver_id})
    # if receiver:
    # receiver_balance_before = receiver["balance"]
    # receiver_log_path = setup_logging(receiver)
    # log_message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - "
    # log_message += "INFO - " if success else "ERROR - "
    # log_message += f"Transaction {'successful' if success else 'failed'}, amount={amount}, "
    # log_message += f"Before_balance: {balance},After_balance:, "
    # log_message += "route:transaction/transaction\n"
    
    # with open(receiver_log_path, 'a') as log_file:
    #     log_file.write(log_message)
    

    

redis =Redis(
  host='redis-19175.c14.us-east-1-2.ec2.redns.redis-cloud.com',
  port=19175,
  password='SUgs1JXtonLW8gV35QmNCNSOfKDq00gt')

concurrency_limit = 1
semaphore = asyncio.Semaphore(concurrency_limit)

async def process_transaction(job, token=None):
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
        log_transaction(send["user_id"],f"Before transaction-{send["balance"]}",data["amount"],"transaction/transaction")
        log_transaction(receive["user_id"],f"Before transaction-{receive["balance"]}",data["amount"],"transaction/transaction")
        
        
        print(f"Sender balance before: {send['balance']}")
        print(f"Receiver balance before: {receive['balance']}")

        # log_transaction(send["user_id"],send["balance"],data["amount"], success=True)
        # log_transaction(receive["user_id"],receive["balance"],data["amount"], success=True)
        
        send["cashout_daily_used"] += data["amount"]
        send["cashout_monthly_used"] += data["amount"]
        send["cashout_yearly_used"] += data["amount"]
        send["balance"]-= data["amount"]
        sender=collection.find_one_and_update({"user_id": send["user_id"]}, {"$set": send},return_document=True)
        


        receive["cashin_daily_used"] += data["amount"]
        receive["cashin_monthly_used"] += data["amount"]
        receive["cashin_yearly_used"] += data["amount"]
        receive["balance"] += data["amount"]
        receiver=collection.find_one_and_update({"user_id": receive["user_id"]}, {"$set": receive},return_document=True)

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
        log_transaction(send["user_id"],f'After_transaction-{sender["balance"]}',data["amount"],"transaction/transaction")
        log_transaction(receive["user_id"],f'After_transaction-{receiver["balance"]}',data["amount"],"transaction/transaction")
        
        
        print("Transaction processed successfully:", data)
    except Exception as err:
        log_transaction(send["user_id"],send["balance"],data["amount"])
        log_transaction(receive["user_id"],receive["balance"],data["amount"])
        
        raise err

worker = Worker(name="myQueue", processor=process_transaction, opts={"connection":redis})


