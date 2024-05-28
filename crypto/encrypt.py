from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
import base64
import json

class Crypto:
    def __init__(self):
        password = "xyzcrypoPROJECT123XYZCRYPTOpass"
        salt = "123xyzCRYPTOprojectSALT123xYZ"
        self.key = PBKDF2(password, salt, dkLen=32, count=100)

    def encrypt(self, data):
        try:
            cipher = AES.new(self.key, AES.MODE_GCM)
            ciphertext, tag = cipher.encrypt_and_digest(data.encode())
            return base64.b64encode(cipher.nonce + tag + ciphertext).decode()
        except Exception as e:
            print("Error during encryption:", e)
            return 'error'
   
    def decrypt(self, data):
        try:
            data = base64.b64decode(data.encode())
            nonce = data[:16]
            tag = data[16:32]
            ciphertext = data[32:]
            cipher = AES.new(self.key, AES.MODE_GCM, nonce)
            decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)
            return decrypted_data.decode()
        except Exception as e:
            print("Error during decryption:", e)
            return 'error'
   
    def encrypt_obj(self, obj):
        try:
            json_data = json.dumps(obj)
            cipher = AES.new(self.key, AES.MODE_GCM)
            ciphertext, tag = cipher.encrypt_and_digest(json_data.encode())
            return base64.b64encode(cipher.nonce + tag + ciphertext).decode()
        except Exception as e:
            print("Error during encryption:", e)
            return 'error'

    def decrypt_obj(self, data):
        try:
            data = base64.b64decode(data.encode())
            nonce = data[:16]
            tag = data[16:32]
            ciphertext = data[32:]
            cipher = AES.new(self.key, AES.MODE_GCM, nonce)
            decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)
            json_obj = json.loads(decrypted_data.decode())
            return json_obj
        except Exception as e:
            print("Error during decryption:", e)
            return 'error'