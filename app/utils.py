from passlib.context import CryptContext

#define default password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#hash password
def hash(password: str):
    return pwd_context.hash(password)

#verify password hashes
def verify(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)