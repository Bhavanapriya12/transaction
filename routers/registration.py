from validators.user_validator import registration
from fastapi import Depends
from fastapi import APIRouter
from database import collection
from starlette import status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from datetime import datetime,timedelta
import json
from routers.bot import alert_dev
from crypto.encrypt import crypto
import asyncio
from crypto.tigerbalm import tige
from routers.hash_functions import get_password_hash
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

import random
import uuid
import string
from routers.redis_function import redis
from routers.login_functions import authenticate_user,create_access_token,get_current_user
from routers.redis_function import set_user_in_redis,delete_user_from_redis,get_user_from_redis,user_exists_in_redis

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="registration/token")


router=APIRouter(prefix="/registration",tags=["registration"])

def generate_user_id():
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=3))
    uuid_string = str(uuid.uuid4()).replace('-', '')[:3]
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
        "balance":data.balance
    }
    user_id = generate_user_id()
    await set_user_in_redis(user_id,registration_record)
    registration_record["user_id"]=user_id

    collection.insert_one(registration_record)  
    return JSONResponse({"message": "Registration successful"}, status_code=status.HTTP_201_CREATED)
    
# rate_limit:None=Depends(RateLimiter(times=2, seconds=60))
@router.post("/token")
async def user_login(form_data: OAuth2PasswordRequestForm = Depends(),rate_limit:None=Depends(RateLimiter(times=2, seconds=60))):
    await asyncio.sleep(30)
    login_user = await authenticate_user(form_data.username, form_data.password)
    print(login_user)
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