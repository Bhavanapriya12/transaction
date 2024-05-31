import requests
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import HTTPException


payload = {'username': 'Sravani', 'password': 'Sravani123'}
response = requests.post("http://127.0.0.1:8000/registration/token", data=payload)
print(response)
if response.status_code == 200:
    data = response.json()
    access_token = data.get("access_token")
    # print(access_token)
    # print("POST Request Successful")
    print(data)

    header={"token":access_token}
    response = requests.get('http://127.0.0.1:8000/transaction/balance',headers=header)
    data = response.json()
    if data:
        # print("GET Request Successful")
        print(data)
    else:
        raise HTTPException(status_code=404, detail="User not found")
else:
    raise HTTPException(status_code=429,detail="too many requests")