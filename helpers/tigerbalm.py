from binascii import hexlify, unhexlify
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA512
import json
class TigerBalm:
    def __init__(self):
        self.salt='123xyzTIGerprojectSALT123xYZ'
        self.password='xyztigerPROJECT123XYZCRYPTOpass'
    def __pad(self,text):
        text_length = len(text)
        amount_to_pad = AES.block_size - (text_length % AES.block_size)
        if amount_to_pad == 0:
            amount_to_pad = AES.block_size
        pad = chr(amount_to_pad)
        return text + pad * amount_to_pad

    def __unpad(self,text):
        pad = ord(text[-1])
        return text[:-pad]

    def __cipher(self,salt, password):
        key = PBKDF2(password, salt, 24, count=5000, hmac_hash_module=SHA512)
        iv = bytes.fromhex('00000000000000000000000000000000')
        return AES.new(key, AES.MODE_CBC, iv)

    def encrypt(self, data):
        return hexlify(self.__cipher(self.salt, self.password).encrypt(self.__pad(data).encode('utf8')))

    def decrypt(self, data):
        try:

            # print('--->',self.__cipher(self.salt, self.password).decrypt(unhexlify(data)))
            decrypted_data=self.__unpad(self.__cipher(self.salt, self.password).decrypt(unhexlify(data)).decode('utf8'))
            if decrypted_data is None:
                raise ValueError("Decryption failed. Data may be corrupted or invalid.")
            return decrypted_data
        except Exception as e:
            raise ValueError("Decryption failed. Error: {}".format(str(e)))
    def encrypt_obj(self, data):
        return hexlify(self.__cipher(self.salt, self.password).encrypt(self.__pad(json.dumps(data)).encode('utf8')))

    def decrypt_obj(self, data):
        return json.loads(self.__unpad(self.__cipher(self.salt, self.password).decrypt(unhexlify(data)).decode('utf8')))

tige = TigerBalm()