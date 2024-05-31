from fastapi import Depends,APIRouter
from database import collection
from starlette import status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from redis.asyncio import Redis
from crypto.encrypt import crypto
from routers.login_functions import get_current_user
from bull.work import process_transaction
import json
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from bull.que import queue,add
from routers.bot import alert_dev
from routers.redis_function import redis,get_user_from_redis,set_user_in_redis,delete_user_from_redis,user_exists_in_redis


router=APIRouter(prefix="/transaction",tags=["transaction"])
# rate_limit: None = Depends(RateLimiter(times=5, seconds=60))
@router.get("/balance")
async def get_account_balance(user:dict=Depends(get_current_user),rate_limit: None = Depends(RateLimiter(times=2, seconds=60))):
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
        balance=crypto.encrypt(user["balance"])
        return JSONResponse({"message": "Balance fetched successfully", "data": balance}, status_code=status.HTTP_200_OK)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"user not found for user_id to get the balance-->{user.get('user_id')}")
@router.put("/transaction")
async def send_amount(user_id: str, amount: int,user:dict=Depends(get_current_user)):
    sender=user.get("user_id")
    use= await user_exists_in_redis(sender)
    if use:
        receiver=await user_exists_in_redis(user_id)
        if  await redis.hget(sender,"balance") < str(amount):
            raise HTTPException(status_code=400, detail="Insufficient balance")
        
        r=await add("transaction", {"sender": sender, "receiver":user_id, "amount": amount},1)
        print(f"queue added-->{r}")
        return {"message": "Transaction request enqueued for processing"}

    sender = collection.find_one({"user_id": user.get("user_id")})
    print(sender)
    if not sender:
        raise HTTPException(status_code=404, detail=f"User not found for sender user_id")
    receiver=collection.find_one({"user_id": user_id})
    if not receiver:
        raise HTTPException(status_code=404, detail=f"User not found for receiver user_id")
    if sender["balance"] < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    r=await add("transaction", {"sender": sender["user_id"], "receiver":user_id, "amount": amount},1)
    print(f"queue added-->{r}")
    return {"message": "Transaction request enqueued for processing"}