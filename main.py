from fastapi import FastAPI
from routers import registration,transaction,bot
from fastapi import Request,HTTPException,status
from fastapi.exceptions import RequestValidationError
from pymongo.errors import ConnectionFailure as MongoConnectionError
from redis.exceptions import ConnectionError as RedisConnectionError
from fastapi.responses import JSONResponse
from telegram import Bot
import logging
from routers.bot import alert_dev
import traceback

app=FastAPI(debug=True)

@app.middleware("http")
async def handle_exceptions(req: Request, next):
    try:
        res = await next(req)
        return res
    except HTTPException as http_exception:
        alert_dev(f"HTTP Exception: {http_exception.detail}")
        raise HTTPException(status_code=http_exception.status_code, detail=str(http_exception.detail))
    except Exception as err:
        alert_dev(f"Error occurred:❌❌❌❌ {str(err)}")
        print(err)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(err)}")

app.include_router(registration.router)
app.include_router(transaction.router)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

