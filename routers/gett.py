
import requests
from fastapi import HTTPException
import time


total_requests = 10
total_seconds = 10
time_between_requests = total_seconds / total_requests


# async def post(payload):


#     for _ in range(total_requests):
#         payload = {'username': 'Sravani', 'password': 'Sravani123'}
#         response = requests.post("https://transaction-6.onrender.com/registration/token", data=payload)
#         print(response)
#         if response.status_code == 200:
#             data = response.json()
#             # access_token = data.get("access_token")
#             time.sleep(time_between_requests)
            
#             print(data.access_token)
#             print("POST Request Successful")
#             return data
#         else:
#             raise HTTPException(status_code=response.status_code, detail=response.text)
# async def get(access_token):
    
#     for _ in range(total_requests):
#         header={"token":access_token}
#         response = requests.get('https://transaction-6.onrender.com/transaction/balance',headers=header)
#         data = response.json()
#         time.sleep(time_between_requests)
#         if data:
#             return data
#         else:
#             raise HTTPException(status_code=response.status_code, detail=response.text)


otal_requests = 10
total_seconds = 10
time_between_requests = total_seconds / total_requests

for _ in range(total_requests):
    payload = {'username': 'Sravani', 'password': 'Sravani123'}
    response = requests.post("https://transaction-6.onrender.com/registration/token", data=payload)
    print(response)
    if response.status_code == 200:
        data = response.json()
        access_token = data.get("access_token")
        time.sleep(1)
        
        # print(access_token)
        # print("POST Request Successful")
        print(data)

        header={"token":access_token}
        response = requests.get('https://transaction-6.onrender.com/transaction/balance',headers=header)
        data = response.json()
        if data:
            # print("GET Request Successful")
            print(data)
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        time.sleep(1)
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)