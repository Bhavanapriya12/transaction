from database import collection
from starlette import status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime,timedelta
from typing import Optional
from redis.asyncio import Redis
from routers.hash_functions import verify_password
import json
import jwt
from fastapi import Header
from routers.redis_function import redis



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="registration/token")


JWT_ENCODING_ALGORITHM = 'HS256'
JWT_EXPIRY_WINDOW_IN_HOURS = 24
JWT_SECRET_KEY = "MhvR7A0r9MObSekgMqvDH84rr1wAQtD/w5tZNYF2t98="

async def authenticate_user(username: str, password: str):
    user_data = await redis.hget(username,"registration_record")
    
    if user_data:
        user_data = json.loads(user_data)
        print(user_data)
        if verify_password(password, user_data['password']):
            return user_data
        else:
            raise HTTPException(status_code=404, detail="User not found or invalid username or password")
    
    user = collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found or invalid username or password")
    if not verify_password(password, user.get("password")):
        raise HTTPException(status_code=404, detail="User not found or invalid username or password")
    return user

def create_access_token(username: str,user_id:str, email: str,
                        expires_delta: Optional[timedelta] = None):
    encode = {"username": username, "email": email,"user_id":user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({"exp": expire})
    encoded_jwt=jwt.encode(encode, JWT_SECRET_KEY, algorithm=JWT_ENCODING_ALGORITHM)
    print(encoded_jwt)
    return encoded_jwt

def get_current_user(token: str = Header("token")):
    # print("get_current_user called")
    # try:
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ENCODING_ALGORITHM])
    username: str = payload.get("username")
    user_id: str = payload.get("user_id")
    email: str = payload.get('email')
    if email is None:
        raise get_user_exception()

    if user_id is None:
        user = collection.find_one({"email":email})
        if not user:
            raise get_user_exception()
        print(user)
        user_id = user.user_id

    return {'username': username, 'user_id': user_id, 'email': email}
    # except jwt.ExpiredSignatureError:
    #     raise get_user_exception(detail="Token has expired")
    # except jwt.InvalidTokenError:
    #     raise get_user_exception(detail="Invalid token")
    # except Exception as e:
    #     raise get_user_exception()
    

def get_user_exception(detail: str = "Could not validate credentials"):
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"}
    )
