# from helpers.tigerbalm import tige
import uuid
import random
import string

# phone_number="799514733"
# e=tige.encrypt(phone_number)
# print(e)
# d=tige.decrypt(e)


# print(d)



def generate_user_id(str,length):
    s=str.upper()
    random_string = ''.join(random.choices(string.ascii_letters.upper()+string.digits , k=length))
    print(random_string)
    # uuid_string = str(uuid.uuid4()).replace('-', '')[:3]
    # print(uuid_string)
    return s+random_string

s=generate_user_id("user",15)
print(s)