from bcrypt import hashpw, gensalt, checkpw
from flask_httpauth import HTTPBasicAuth
from models import User
from flask import request


auth = HTTPBasicAuth()


def hash_password(password: str):
    byte_password = password.encode()
    hashed_password = hashpw(byte_password, gensalt())
    password = hashed_password.decode()
    return password


def check_password(password: str, hashed_password: str):
    byte_pw = password.encode()
    byte_hashed_pw = hashed_password.encode()
    return checkpw(byte_pw, byte_hashed_pw)


@auth.verify_password
def verify_password(email: str, password: str):
    user = request.db_session.query(User).filter(User.email == email).first()
    if user and check_password(password, user.password):
        return user
