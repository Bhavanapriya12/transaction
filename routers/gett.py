
import requests
from fastapi import HTTPException
import time


total_requests = 10
total_seconds = 10
time_between_requests = total_seconds / total_requests


async def post(payload):


    for _ in range(total_requests):
        payload = {'username': 'Sravani', 'password': 'Sravani123'}
        response = requests.post("http://127.0.0.1:8000/registration/token", data=payload)
        print(response)
        if response.status_code == 200:
            data = response.json()
            # access_token = data.get("access_token")
            time.sleep(time_between_requests)
            
            # print(access_token)
            # print("POST Request Successful")
            return data
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
async def get(access_token):
    
    for _ in range(total_requests):
        header={"token":access_token}
        response = requests.get('http://127.0.0.1:8000/transaction/balance',headers=header)
        data = response.json()
        time.sleep(time_between_requests)
        if data:
            return data
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)