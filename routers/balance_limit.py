from validators.user_validator import CashLimit
from database import limit
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException


def cash(data:CashLimit,user_id,amount,cash_type):
    # data:CashLimit
    if cash_type=="debit":
        user=limit.find_one({"user_id":user_id})
        print(user)
        if user:
            if amount > user["cashout_daily_limit"] or amount > user["cashout_monthly_limit"] or amount > user["cashout_yearly_limit"]:
                raise HTTPException(status_code=400,detail="limit exceeded")
            elif user["cashout_daily_limit"] == user["cashout_daily_used"] or user["cashout_monthly_limit"] == user["cashout_monthly_used"] or user["cashout_yearly_limit"] == user["cashout_yearly_used"]:
                raise HTTPException(status_code=400,detail="limit exceeded")
            elif user["cashout_daily_limit"] - user["cashout_daily_used"] < amount or user["cashout_monthly_limit"] - user["cashout_monthly_used"] < amount or user["cashout_yearly_limit"] - user["cashout_yearly_used"] < amount:
                raise HTTPException(status_code=400,detail="limit exceeded")
            else:
                user["cashout_daily_used"]+=amount
                user["cashout_monthly_used"]+=amount
                user["cashout_yearly_used"]+=amount
                limit.update_one({"user_id":user_id}, {"$set": user})
                return JSONResponse({"message": "limit updated"},status_code=200)
        else:
            limit_record={"user_id":user_id,
                            "cashout_daily_used":amount,
                            "cashout_monthly_used":amount,
                            "cashout_yearly_used":amount,
                            "cashout_daily_limit":data.cashout_daily_limit,
                            "cashout_monthly_limit":data.cashout_monthly_limit,
                            "cashout_yearly_limit":data.cashout_yearly_limit,
                            "cashin_daily_limit":data.cashin_daily_limit,
                            "cashin_monthly_limit":data.cashin_monthly_limit,
                            "cashin_yearly_limit":data.cashin_yearly_limit,
                            "cashin_daily_used":data.cashin_daily_used,
                            "cashin_monthly_used":data.cashin_monthly_used,
                            "cashin_yearly_used":data.cashin_yearly_used
                            }
            limit.insert_one(limit_record)
            return JSONResponse(status_code=200, content={"message": "limit added"})
    
    elif cash_type=="credit":
        user=limit.find_one({"user_id":user_id})
        if user:
            if amount > user["cashin_daily_limit"] or amount > user["cashin_monthly_limit"] or amount > user["cashin_yearly_limit"]:
                raise HTTPException(status_code=400, detail="limit exceeded")
            elif user["cashin_daily_limit"] == user["cashin_daily_used"] or user["cashin_monthly_limit"] == user["cashin_monthly_used"] or user["cashin_yearly_limit"] == user["cashin_yearly_used"]:
                raise HTTPException(status_code=400,detail="limit exceeded")
            elif (user["cashin_daily_limit"] - user["cashin_daily_used"] < amount) or (user["cashin_monthly_limit"] - user["cashin_monthly_used"] < amount) or (user["cashin_yearly_limit"] - user["cashin_yearly_used"] < amount):
                raise HTTPException(status_code=400, detail="limit exceeded")
            else:
                user["cashin_daily_used"]+=amount
                user["cashin_monthly_used"]+=amount
                user["cashin_yearly_used"]+=amount
                limit.update_one({"user_id":user_id}, {"$set": user})
                return JSONResponse(status_code=200, content={"message": "limit updated"})
    
        limit_record={"user_id":user_id,
                        "cashout_daily_used":data.cashout_daily_used,
                        "cashout_monthly_used":data.cashout_monthly_used,
                        "cashout_yearly_used":data.cashout_yearly_used,
                        "cashout_daily_limit":data.cashout_daily_limit,
                        "cashout_monthly_limit":data.cashout_monthly_limit,
                        "cashout_yearly_limit":data.cashout_yearly_limit,
                        "cashin_daily_limit":data.cashin_daily_limit,
                        "cashin_monthly_limit":data.cashin_monthly_limit,
                        "cashin_yearly_limit":data.cashin_yearly_limit,
                        "cashin_daily_used":amount,
                        "cashin_monthly_used":amount,
                        "cashin_yearly_used":amount,
                 }
        limit.insert_one(limit_record)
        return JSONResponse(status_code=200, content={"message": "limit added"})
    else:
        raise HTTPException(status_code=404, detail="invalid arguments")


