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
from crypto.encrypt import Crypto
import random
import uuid
import string
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
    # email =  collection.find_one({"email": data.email})
    # if email and email["status"]=="enable":
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error occurred in user registration.Email already exists")
    # phone_number = collection.find_one({"phone_number": data.phone_number})
    # print(phone_number)
    # if phone_number and phone_number["status"]=="enable":
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error occurred in user registration.Phone number already exists")
    try:

        registration_record={
            "password":data.password,
            "username":data.username,
            "email":data.email,
            "phone_number":data.phone_number,
            "status":"enable",
            "balance":data.balance
        }
        user_id = generate_user_id()
        registration_record["user_id"] = user_id
        Crypto.encrypt_obj(Crypto(),registration_record)
        
        # inserted_result = collection.insert_one(registration_record)
        # inserted_id = str(inserted_result.inserted_id)
        # data_dict["_id"]=inserted_id
        # await set_user_in_redis(f"{data_dict["user_id"]}",(data_dict))
        
        return JSONResponse({"message": "Registration successful"}, status_code=status.HTTP_201_CREATED)
    except Exception as e:
        alert_dev(f"Error occurred:❌❌❌❌ {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/token")
async def user_login(form_data: OAuth2PasswordRequestForm = Depends()):
    login_user = await authenticate_user(form_data.username, form_data.password)
    # print(user)
    if not login_user or login_user.get("status") == "disable":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    try:
        token_expires = timedelta(15)
        token = create_access_token(login_user["username"], login_user["user_id"],login_user["email"] ,expires_delta=token_expires)

        return {"access_token": token, "token_type": "Bearer"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))


@router.delete("/delete_user")
async def delete_user(user_id:str):
    use=await user_exists_in_redis(user_id)
    if use:
        await delete_user_from_redis(user_id)
    user=collection.find_one({"user_id":user_id})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="user not found for user_id-->{user_id} in delete user by id api ")
    delete=collection.find_one({"user_id":user_id})
    if  delete and delete.get("status")=="disable":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='user not found for user_id-->{user_id} in delete user by id api ')
    try:
        delete=collection.find_one({"user_id":user_id})
        collection.find_one_and_update({"user_id":user_id},{"$set":{"status":"disable"}})
        return JSONResponse({"message":"successfully deleted the user"},status_code=status.HTTP_200_OK)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))
    
@router.get("/get_user")
async def get_user(user_id:str):
    # user= await user_exists_in_redis(user_id)
    # print(user)
    # if user:
    #     s=await get_user_from_redis(user_id)
    #     return JSONResponse({"message":"successfully retrieved user by user id","data":s},status_code=status.HTTP_200_OK)
    # user=collection.find_one({decrypt(data["user_id"]):user_id})
    # if not user or user.get("status")=="disable":
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"user not found for user_id-->{user_id} in get user based on user id api ")
    # try:
    user_records=collection.find_one({"user_id":user_id})
    #     user['_id'] = str(user['_id'])
    #     await set_user_in_redis(user_id, user)
    #     print(user)
    #     return JSONResponse({"message":"successfully retrieved user by user id","data":user},status_code=status.HTTP_200_OK)
    # except Exception as e:
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))
        # user_records = collection.find()
            
    if not user_records:
        # If user not found, raise HTTP 404 error
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found for user_id {user_id}"
        )
    
    if 'encrypted_data' not in user_records:
        # If encrypted_data not found in user_record, raise HTTP 404 error
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Encrypted data not found for user_id {user_id}"
        )

    # Decrypt the encrypted data
    decrypted_data = await decrypt(
        user_records["salt"],user_records["iv"],user_records["encrypted_data"]
    )

    # Return the decrypted user data
    return JSONResponse(
        {"message": "Successfully retrieved user by user id", "data": decrypted_data},
        status_code=status.HTTP_200_OK
    )
    
    # except HTTPException as http_error:
    #     # Re-raise HTTP exceptions
    #     raise http_error
    
    # except Exception as e:
    #     # Catch any other exceptions and return HTTP 500 error
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail=str(e)
    #     )