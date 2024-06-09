from fastapi import FastAPI
from routers import registration,transaction
from fastapi import Request,HTTPException,status
from fastapi.exceptions import RequestValidationError
from pymongo.errors import ConnectionFailure as MongoConnectionError
from redis.exceptions import ConnectionError as RedisConnectionError
from fastapi.responses import JSONResponse
from fastapi import Depends
from database import collection
from routers.login_functions import get_current_user
# from telegram import Bot
from fastapi_utilities import repeat_every,repeat_at
import logging
from routers.bot import alert_dev
import traceback
from routers.redis_function import redis
from fastapi_limiter import FastAPILimiter
from fastapi import Header
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from routers.balance_limit import daily
from bull import work
import aiocron
from aiocron import crontab
import asyncio

@asynccontextmanager
async def startup(app: FastAPI):
    global daily
    print("app started")
    # daily.start()
    daily()
    
    await FastAPILimiter.init(redis,identifier=identifier)
    print("start")
    # cron=crontab("10 * * * * *", func=daily)
    # cron.start()

    # print(cron)
    
    
    # monthly()
    # daily()
    # monthly.start()
    # yearly.start()
    # await 
    yield
    print("app shut down...")

app=FastAPI(debug=True,lifespan=startup)



origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.middleware("http")
# async def handle_exceptions(req: Request, next):
#     try:
#         res = await next(req)
#         return res
#     except HTTPException as http_exception:
#         alert_dev(f"HTTP Exception: {http_exception.detail}")
#         raise HTTPException(status_code=http_exception.status_code, detail=str(http_exception.detail))
#     except Exception as err:
#         alert_dev(f"Error occurred:❌❌❌❌ {str(err)}")
#         print(err)
#         raise HTTPException(status_code=500, detail=f"Internal server error: {str(err)}")

app.include_router(registration.router)
app.include_router(transaction.router)
# app.include_router(balance_limit.router)



async def identifier(request):
    # if request.headers
    # if request.headers
    token = request.headers.get("token")
    if token:
        token_bytes = token.encode('utf-8') 
        user = get_current_user(token_bytes)
        if user:
            user_id = user.get("user_id")
            return user_id
        raise HTTPException(status_code=401, detail="Unauthorized")
    else:
        print(request.client.host)
        return request.client.host


if __name__ == "__main__":
    import uvicorn
    from routers import redis_function
    # daily.start()
    # asyncio.get_event_loop().run_forever()
    uvicorn.run(app, host="0.0.0.0", port=8000)

