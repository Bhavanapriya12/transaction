from fastapi import Depends,APIRouter
from database import collection
from starlette import status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from redis.asyncio import Redis
from helpers.encrypt import crypto
from routers.login_functions import get_current_user
from bull.work import process_transaction
from fastapi_limiter.depends import RateLimiter
from validators.user_validator import transaction
import json
from bull.que import queue,add
from routers.balance_limit import cash
from routers.bot import alert_dev
from routers.redis_function import redis,get_user_from_redis,set_user_in_redis,delete_user_from_redis,user_exists_in_redis
from bull.work import setup_logging,read_log_file
from datetime import datetime
from database import db
import pyminizip
import os
from zipfile import ZipFile
import pyzipper
from fastapi.responses import FileResponse
import subprocess
from bson.objectid import ObjectId



# with pyzipper.ZipFile(f"{output_folder}.zip", 'w', compression=pyzipper.ZIP_DEFLATED) as zip:
#     # Set password for encryption (optional)
#         password = zip_password.encode('utf-8')
#         zip.setpassword(password)
    


password="collection"
zip_password=bytes(password.encode('utf-8'))

router=APIRouter(prefix="/transaction",tags=["transaction"])
# rate_limit: None = Depends(RateLimiter(times=5, seconds=60))
@router.get("/balance")
async def get_account_balance(user:dict=Depends(get_current_user),rate_limit: None = Depends(RateLimiter(times=10, seconds=10))):
    user_id=user.get("user_id")
    # await FastAPILimiter.init(redis,identifier=user_id)
    print(user_id)
    use= await user_exists_in_redis(user_id)
    if use:
        s=await redis.hget(user_id ,"balance")
        # r=crypto.encrypt(s)
        print(s)
        return JSONResponse({"message": "Balance fetched successfully", "data": s}, status_code=status.HTTP_200_OK)
    
    user=collection.find_one({"user_id":user.get("user_id")})
    if user:
        balance=user["balance"]
        return JSONResponse({"message": "Balance fetched successfully", "data": balance}, status_code=status.HTTP_200_OK)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"user not found for user_id to get the balance-->{user.get('user_id')}")
@router.put("/transaction")
async def send_amount(data:transaction,user:dict=Depends(get_current_user)):
    # sender=user.get("user_id")
    # use= await user_exists_in_redis(sender)
    # if use:
    #     receiver=await user_exists_in_redis(data.user_id)
    #     if  await redis.hget(sender,"balance") < str(data.amount):
    #         raise HTTPException(status_code=400, detail="Insufficient balance")
        
    #     r=await add("transaction", {"sender": sender, "receiver":data.user_id, "amount": data.amount},1)
    #     print(f"queue added-->{r}")
    #     return {"message": "Transaction request enqueued for processing"}

    sender = collection.find_one({"user_id": user.get("user_id")})
    print(sender)
    if not sender:
        raise HTTPException(status_code=404, detail=f"User not found for sender user_id")
    receiver=collection.find_one({"user_id": data.user_id})
    if not receiver:
        raise HTTPException(status_code=404, detail=f"User not found for receiver user_id")
    if sender["balance"] < data.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    response=await cash(sender["user_id"],receiver["user_id"],data.amount)
    if response["status_code"] == 400:
        print(response["status_code"])
        raise HTTPException(status_code=response["status_code"], detail=response["message"])
    
    r=await add("transaction",{ "sender": sender["user_id"], "receiver":data.user_id, "amount": data.amount,"payment_category":data.payment_category}, 1)
    print(f"queue added-->{r.data}")
    await process_transaction(r)
    return {"message": "transaction request enqueued for processing"}



@router.get("/get_logs")
async def get_logs(user_id:str,date:datetime):

    # user=collection.find_one({"user_id":user.get("user_id")})
    # if not user:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"user not found for user_id to get the balance-->{user.get('user_id')}")
    log_file_path = setup_logging(user_id, date)
    logs = read_log_file(log_file_path)
    
    if not logs:
        raise HTTPException(status_code=404, detail="Log file not found")

    return JSONResponse({"message": "Logs fetched successfully", "data": logs}, status_code=status.HTTP_200_OK)
@router.get("/get_collections")
async def get_collections():
    collections = db.list_collection_names()
    output_folder = "collection_data"
    zip_filename=f'{output_folder}.zip'
    os.makedirs(output_folder, exist_ok=True)

    for collection_name in collections:
        collection_data = db[collection_name].find()
        with open(f"{output_folder}/{collection_name}.json", "w") as f:
            for document in collection_data:
                document["phone_number"]=str(document['phone_number'])
                document['_id'] = str(document['_id'])
                doc=json.dumps(document)
                f.write(doc + "\n")
    # print('output_folder--->',os.getcwd()+'\\'+output_folder)
    # pyminizip.compress(output_folder, None,zip_filename, password, 5)
    with pyzipper.AESZipFile('output.zip', 'w', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as zip:
        zip.pwd = zip_password
    #     zip.pwd = b'password'
    # with ZipFile(f"{output_folder}.zip", 'w') as zip:
        for root, dirs, files in os.walk(output_folder):
            for file in files:
                file_path = os.path.join(root, file)
                zip.write(file_path, os.path.relpath(file_path, output_folder))
            
    return JSONResponse({"message": "Collections fetched successfully", "data": collections}, status_code=status.HTTP_200_OK)

# @router.get("/get_collections")
# async def get_collections():
#     collections = db.list_collection_names()
#     output_folder = "collection_data"
#     zip_filename=f'{output_folder}.zip'
#     os.makedirs(output_folder, exist_ok=True)
#     current_directory = os.getcwd()

#     folder_path = os.path.join(current_directory, output_folder)
#     print(folder_path)

#     for collection_name in collections:
#         collection_data = db[collection_name].find()
#         with open(f"{output_folder}/{collection_name}.json", "w") as f:
#             for document in collection_data:
#                 document["phone_number"]=str(document['phone_number'])
#                 document['_id'] = str(document['_id'])
#                 doc=json.dumps(document)
#                 f.write(doc + "\n")
#     # print('output_folder--->',os.getcwd()+'\\'+output_folder)
#     pyminizip.compress(output_folder, None,zip_filename, password, 5)

            
#     return JSONResponse({"message": "Collections fetched successfully", "data": collections}, status_code=status.HTTP_200_OK)
