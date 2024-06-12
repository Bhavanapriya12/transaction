from validators.user_validator import registration
from fastapi import Depends
from fastapi import APIRouter
from database import collection
from starlette import status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from datetime import datetime,timedelta
import os
import json
from routers.bot import alert_dev
from helpers.encrypt import crypto
import base64
import asyncio
from helpers.tigerbalm import tige
from routers.hash_functions import get_password_hash
# from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from database import history
import pandas as pd
from openpyxl import Workbook
from fastapi.responses import FileResponse
from fastapi import UploadFile,File
import random
import uuid
import string
from bson import Binary
from base64 import b64encode
from routers.redis_function import redis
from routers.login_functions import authenticate_user,create_access_token,get_current_user
from routers.redis_function import set_user_in_redis,delete_user_from_redis,get_user_from_redis,user_exists_in_redis

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="registration/token")


router=APIRouter(prefix="/registration",tags=["registration"])

def generate_user_id():
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=3))
    print(random_string)
    uuid_string = str(uuid.uuid4()).replace('-', '')[:3]
    print(uuid_string)
    return random_string + uuid_string

def generate_transaction_id():
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=2))
    uuid_string = str(uuid.uuid4()).replace('-', '')[:3]
    return random_string + uuid_string

@router.post("/user_registration")
async def user_register(data: registration):
    password=get_password_hash(data.password)
    phone_number=tige.encrypt(data.phone_number)

    registration_record={
        "password":password,
        "username":data.username,
        "email":data.email,
        "phone_number":phone_number,
        "status":"enable",
        "balance":data.balance,
        "cashout_daily_limit":data.cashout_daily_limit,
        "cashout_monthly_limit":data.cashout_monthly_limit,
        "cashout_yearly_limit":data.cashout_yearly_limit,
        "cashout_daily_used":data.cashout_daily_used,
        "cashout_monthly_used":data.cashout_monthly_used,
        "cashout_yearly_used":data.cashout_yearly_used,
        "cashin_daily_limit":data.cashin_daily_limit,
        "cashin_monthly_limit":data.cashin_monthly_limit,
        "cashin_yearly_limit":data.cashin_yearly_limit,
        "cashin_daily_used":data.cashin_daily_used,
        "cashin_monthly_used":data.cashin_monthly_used,
        "cashin_yearly_used":data.cashin_yearly_used,

    }
    user_id = generate_user_id()
    await set_user_in_redis(user_id,registration_record)
    registration_record["user_id"]=user_id
    phone=tige.decrypt(registration_record["phone_number"])

    collection.insert_one(registration_record)  
    return JSONResponse({"message": "Registration successful","data":phone}, status_code=status.HTTP_201_CREATED)
    
# rate_limit:None=Depends(RateLimiter(times=2, seconds=60))
@router.post("/token")
async def user_login(form_data: OAuth2PasswordRequestForm = Depends(),rate_limit:None=Depends(RateLimiter(times=10, seconds=10))):
    login_user = await authenticate_user(form_data.username, form_data.password)
    # print(login_user)
    if not login_user or login_user.get("status") == "disable":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    token_expires = timedelta(15)
    token = create_access_token(login_user["username"], login_user["user_id"],login_user["email"] ,expires_delta=token_expires)

    return {"access_token": token,"token_type": "bearer"}
@router.delete("/delete_user")
async def delete_user(user_id:str):
    use=await user_exists_in_redis(user_id)
    if use:
        await delete_user_from_redis(user_id)
    delete=collection.find_one({"user_id":user_id})
    if  delete and delete.get("status")=="disable":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='user not found for user_id-->{user_id} in delete user by id api ')
    collection.find_one_and_update({"user_id":user_id},{"$set":{"status":"disable"}})
    return JSONResponse({"message":"successfully deleted the user"},status_code=status.HTTP_200_OK)

@router.get("/get_user")
# @RateLimiter(times=10,minutes=1)
async def get_user(user_id: str):
    # Check if the user exists in Redis
    user = await user_exists_in_redis(user_id)
    if user:
        data = await get_user_from_redis(user_id)
        decrypted_phone_number = tige.decrypt(data["phone_number"])
        data["phone_number"] = decrypted_phone_number
        encrypted_data = crypto.encrypt_obj(data)
        return JSONResponse(
            {"message": "Successfully retrieved user by user id", "data": encrypted_data},
            status_code=status.HTTP_200_OK
        )
    user_record = collection.find_one({"user_id": user_id})
    if not user_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found for user_id {user_id}"
        )

    decrypted_phone_number = tige.decrypt(user_record["phone_number"])
    user_record["phone_number"] = decrypted_phone_number

    encrypted_data = crypto.encrypt_obj(user_record)

    return JSONResponse(
        {"message": "Successfully retrieved user by user id", "data": encrypted_data},
        status_code=status.HTTP_200_OK
    )


@router.get("/excel_file")
async def excel_download(user:dict=Depends(get_current_user)):
    user_records= history.find({"user_id": user.get("user_id")})
    # print(user_records)
    if not user_records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found for user_id {user.get('user_id')}"
        )
    
    transaction_data=[dict(user_record) for user_record in user_records]
    for transactions in transaction_data:
        transactions["_id"] = str(transactions["_id"])
        transactions["phone_number"]=tige.decrypt(transactions["phone_number"])

    

    
    output = "transactions.xlsx"
    df=pd.DataFrame(transaction_data)
    df.drop(columns=["_id"], inplace=True)
    print(df)

    wb = Workbook()
    ws = wb.active
    ws.append(df.columns.tolist())
    for row in df.itertuples(index=False, name=None):
        ws.append(row)


    # pd.ExcelWriter("transactions.xlsx")
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False)
    wb.save(output)
    # print(output)

    return FileResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",filename=output)
    


@router.post("/upload_image")
async def upload_image(image_file:UploadFile=File(...),user:dict=Depends(get_current_user)):


    user_id=user.get("user_id")
    user=collection.find_one({"user_id":user_id})
    # print(user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found for user_id {user_id}"
        )
    image_data = await image_file.read()
    if len(image_data) > 141*1024:
        print(len(image_data))
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "Image size exceeds 141kb."})
    print(len(image_data))
    FOLDER = "images/" + user_id
    folder_path = os.path.join(os.getcwd(), FOLDER)
    print(folder_path)
    os.makedirs(folder_path, exist_ok=True)
    
    
    
    image_path = os.path.join(folder_path, image_file.filename)

    with open(image_path, "wb") as file:
        file.write(image_data)

    base64_encoded_data = base64.b64encode(image_data).decode('utf-8')
    data_url = f"data:image/png;base64,{base64_encoded_data}"

    
    # data= base64_encoded_data
    # print(data_url)

    collection.update_one({'user_id': user_id}, {'$set': {'image': data_url}})
    
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Image uploaded successfully"}) 