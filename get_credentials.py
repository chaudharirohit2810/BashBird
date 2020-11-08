from cryptography.fernet import Fernet
import getpass
from dotenv import load_dotenv
import os
import sys


class Credentials:
    '''Class which stores and retrievies email and password of user'''

    __dir_path = ""
    __env_path = ""

    def __init__(self):
        user = getpass.getuser()

        self.__dir_path = os.path.join("/home", user, ".termmail")
        self.__env_path = os.path.join(self.__dir_path, ".env")

    def __create_key(self):
        '''Create a encryption key if it does not exist'''

        key_file_name = '.termmailkey.key'
        key_path = os.path.join(self.__dir_path, key_file_name)
        try:
            open(key_path)
        except Exception as e:
            key = Fernet.generate_key()
            key_file = open(key_path, 'wb')
            key_file.write(key)
            key_file.close()

    def __get_key(self):
        '''Get encryption key'''

        key_file_name = '.termmailkey.key'
        key_path = os.path.join(self.__dir_path, key_file_name)
        key = open(key_path, 'rb').read()
        return key

    def get_credentials(self):
        '''Get credentials from .env file'''

        try:
            self.__decrypt_file()
            load_dotenv(self.__env_path)
            password = os.getenv("PASSWORD")
            email = os.getenv("EMAIL")
            os.remove(self.__env_path)
            return True, email, password
        except:
            return False, " ", " "

    def __decrypt_file(self):
        f = Fernet(self.__get_key())
        encrypted_file_path = os.path.join(self.__dir_path, ".env.encrypted")
        with open(encrypted_file_path, 'rb') as test:
            data = test.read()
        credentials = f.decrypt(data).decode()
        with open(self.__env_path, 'w') as env_file:
            env_file.write(credentials)

    def store_credentials(self, email, password):
        '''To store the credentials'''

        fi = open(self.__env_path, "w")
        fi.write("EMAIL=" + email + "\n")
        fi.write("PASSWORD=" + password + "\n")
        fi.close()
        self.__encrypt_file()
        os.remove(self.__env_path)

    def __encrypt_file(self):
        '''To encrypt the .env file'''

        self.__create_key()
        f = Fernet(self.__get_key())
        with open(self.__env_path, 'rb') as test:
            data = test.read()
        encrypted = f.encrypt(data)
        encrypted_file_path = os.path.join(self.__dir_path, ".env.encrypted")
        with open(encrypted_file_path, 'wb') as enc:
            enc.write(encrypted)

    def remote_credentials(self):
        '''To remove credentials on logout'''
        try:
            encrypted_file_path = os.path.join(
                self.__dir_path, ".env.encrypted")
            os.remove(encrypted_file_path)
        except:
            pass


if __name__ == "__main__":
    cred = Credentials()
    cred.store_credentials("Rohit", "Rohit@123")
    # print(cred.get_credentials())
