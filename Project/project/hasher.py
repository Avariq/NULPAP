import hashlib

class HashPassword:
    def __init__(self):
        self.__value = ''

    def Hash(self, password):
        self.__value = password
        encoded_info = self.__value.encode()
        hasher = hashlib.sha256(encoded_info)
        hashed_password = hasher.hexdigest()

        return hashed_password

