# from validators.user_validator import CashLimit
from database import collection
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi_utilities import repeat_every,repeat_at
import aiocron
from aiocron import crontab
from datetime import datetime


async def cash(sender, receiver, amount):
    sender_user = collection.find_one({"user_id": sender})
    print(sender_user)
    if sender_user:
        # if amount > sender_user["cashout_daily_limit"] or amount > sender_user["cashout_monthly_limit"] or amount > sender_user["cashout_yearly_limit"]:
        #     return {"status_code":400,"message":"limit exceeded"}
    
        # elif sender_user["cashout_daily_limit"] == sender_user["cashout_daily_used"] or sender_user["cashout_monthly_limit"] == sender_user["cashout_monthly_used"] or sender_user["cashout_yearly_limit"] == sender_user["cashout_yearly_used"]:
        #     return {"status_code":400,"message":"limit exceeded"}
        # elif sender_user["cashout_daily_limit"] - sender_user["cashout_daily_used"] < amount or sender_user["cashout_monthly_limit"] - sender_user["cashout_monthly_used"] < amount or sender_user["cashout_yearly_limit"] - sender_user["cashout_yearly_used"] < amount:
        #     return {"status_code":400,"message":"limit exceeded"}
        # if amount > sender_user["cashout_daily_limit"]:
        #     return {"status_code": 400, "message": "Daily limit exceeded"}

        # if amount > sender_user["cashout_monthly_limit"]:
        #     return {"status_code": 400, "message": "Monthly limit exceeded"}

        # if amount > sender_user["cashout_yearly_limit"]:
        #     return {"status_code": 400, "message": "Yearly limit exceeded"}

        # if sender_user["cashout_daily_limit"] <= sender_user["cashout_daily_used"]:
        #     return {"status_code": 400, "message": "Daily limit already used up"}

        # if sender_user["cashout_monthly_limit"] <= sender_user["cashout_monthly_used"]:
        #     return {"status_code": 400, "message": "Monthly limit already used up"}

        # if sender_user["cashout_yearly_limit"] <= sender_user["cashout_yearly_used"]:
        #     return {"status_code": 400, "message": "Yearly limit already used up"}

        if sender_user["cashout_daily_limit"] - sender_user["cashout_daily_used"] < amount:
            return {"status_code": 400, "message": "Daily remaining limit insufficient"}

        if sender_user["cashout_monthly_limit"] - sender_user["cashout_monthly_used"] < amount:
            return {"status_code": 400, "message": "Monthly remaining limit insufficient"}

        
        if sender_user["cashout_yearly_limit"] - sender_user["cashout_yearly_used"] < amount:
            return {"status_code": 400, "message": "Yearly remaining limit insufficient"}
        
        # return {"status_code":200,"message":"success"}     

        # sender_user["cashout_daily_used"] += amount
        # sender_user["cashout_monthly_used"] += amount
        # sender_user["cashout_yearly_used"] += amount
        # s=collection.update_one({"user_id": sender}, {"$set": sender_user})
        # if s:
        receiver_user = collection.find_one({"user_id": receiver})
        if not receiver_user:
            return {"status_code":400,"message":"receiver not found"}
        if receiver_user:
            # if amount > receiver_user["cashin_daily_limit"] or amount > receiver_user["cashin_monthly_limit"] or amount > receiver_user["cashin_yearly_limit"]:
            #     return {"status_code":400,"message":"limit exceeded"}
            # elif receiver_user["cashin_daily_limit"] == receiver_user["cashin_daily_used"] or receiver_user["cashin_monthly_limit"] == receiver_user["cashin_monthly_used"] or receiver_user["cashin_yearly_limit"] == receiver_user["cashin_yearly_used"]:
            #     return {"status_code":400,"message":"limit exceeded"}
            # elif receiver_user["cashin_daily_limit"] - receiver_user["cashin_daily_used"] < amount or receiver_user["cashin_monthly_limit"] - receiver_user["cashin_monthly_used"] < amount or receiver_user["cashin_yearly_limit"] - receiver_user["cashin_yearly_used"] < amount:
            #     return {"status_code":400,"message":"limit exceeded"}

            # if amount > receiver_user["cashin_daily_limit"]:
            #     return {"status_code": 400, "message": "Daily limit exceeded"}

            # if amount > receiver_user["cashin_monthly_limit"]:
            #     return {"status_code": 400, "message": "Monthly limit exceeded"}

            # if amount > receiver_user["cashin_yearly_limit"]:
            #     return {"status_code": 400, "message": "Yearly limit exceeded"}

            # if receiver_user["cashin_daily_limit"] <= receiver_user["cashin_daily_used"]:
            #     return {"status_code": 400, "message": "Daily limit already used up"}

            # if receiver_user["cashin_monthly_limit"] <= receiver_user["cashin_monthly_used"]:
            #     return {"status_code": 400, "message": "Monthly limit already used up"}

            # if receiver_user["cashin_yearly_limit"] <= receiver_user["cashin_yearly_used"]:
            #     return {"status_code": 400, "message": "Yearly limit already used up"}

            if receiver_user["cashin_daily_limit"] - receiver_user["cashin_daily_used"] < amount:
                return {"status_code": 400, "message": "Daily remaining limit insufficient"}

            if receiver_user["cashin_monthly_limit"] - receiver_user["cashin_monthly_used"] < amount:
                return {"status_code": 400, "message": "Monthly remaining limit insufficient"}

            if receiver_user["cashin_yearly_limit"] - receiver_user["cashin_yearly_used"] < amount:
                return {"status_code": 400, "message": "Yearly remaining limit insufficient"}

            return {"status_code":200,"message":"success"}
        # # else:
        #     return {"status_code":404,"message":"receiver not found"}
    else:
        return {"status_code":400,"message":"sender not found"}
    
# @aiocron.crontab("10 * * * * *")
@repeat_at(cron="0 0 * * *")
async def daily():
    try:
        print("started cron")
        now = datetime
        print(f"Current: {now}")
        collection.update_many({}, {"$set": {"cashin_daily_used": 0}})

        collection.update_many({}, {"$set": {"cashout_daily_used": 0}})
        print("Daily reset complete")

        now = datetime.now()
        print(f"Current datetime: {now}")
            
        if now.day == 10:
            print("It's the 7th of the month. Performing monthly reset.")
            collection.update_many({}, {"$set": {"cashin_monthly_used": 0}})
            collection.update_many({}, {"$set": {"cashout_monthly_used": 0}})
            print("Monthly reset complete")
        if now.month == 6 and now.day == 10:
            collection.update_many({}, {"$set": {"cashin_yearly_used": 0}})
            collection.update_many({}, {"$set": {"cashout_yearly_used": 0}})
            print("Yearly reset complete")
    except Exception as e:
        print("Error processing transaction:", str(e))

# @repeat_at(cron="1 * * * *")
# async def monthly(): 
#     collection.update_many({}, {"$set": {"cashin_monthly_used": 0}})
#     collection.update_many({}, {"$set": {"cashout_monthly_used": 0}})

# @aiocron.crontab("0 0 1 1 *")
# async def yearly():
#     collection.update_many({}, {"$set": {"cashin_yearly_used": 0}})
#     collection.update_many({}, {"$set": {"cashout_yearly_used": 0}})
    