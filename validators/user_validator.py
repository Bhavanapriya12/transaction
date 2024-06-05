from pydantic import BaseModel, EmailStr, Field,validator
from typing import Optional

class registration(BaseModel):
    username: str
    password: str = Field(..., min_length=8, max_length=64,description="Password must be between 8 and 64 characters")
    email: EmailStr
    phone_number: str = Field(..., min_length=10, max_length=10,description="Phone number must be 10 digits")
    balance: int


class login(BaseModel):
    username: str
    password: str

class transaction(BaseModel):
    amount: int
    user_id: str
    type:Optional[str]
    transaction_id: Optional[str]
    payment_mode: Optional[str]=Field(default="online")
    payment_status: Optional[str]=Field(default="success")
    payment_category: Optional[str]
    transaction_date:Optional[str]
    name: Optional[str]
class CashLimit(BaseModel):
    cashout_daily_limit:int=Field(default=300)
    cashout_monthly_limit:int=Field(default=3000)
    cashout_yearly_limit:int=Field(default=30000)
    cashout_daily_used:int=Field(default=0)
    cashout_monthly_used:int=Field(default=0)
    cashout_yearly_used:int=Field(default=0)
    cashin_daily_limit:int=Field(default=300)
    cashin_monthly_limit:int=Field(default=3000)
    cashin_yearly_limit:int=Field(default=30000)
    cashin_daily_used:int=Field(default=0)
    cashin_monthly_used:int=Field(default=0)
    cashin_yearly_used:int=Field(default=0)


cash_limit = CashLimit(
    cashout_daily_limit=300,
    cashout_monthly_limit=3000,
    cashout_yearly_limit=30000,
    cashout_daily_used=0,
    cashout_monthly_used=0,
    cashout_yearly_used=0,
    cashin_daily_limit=300,
    cashin_monthly_limit=3000,
    cashin_yearly_limit=30000,
    cashin_daily_used=0,
    cashin_monthly_used=0,
    cashin_yearly_used=0,
)