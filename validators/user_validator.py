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