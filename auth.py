import bcrypt


def hash_password(psw: str) -> str:
    return bcrypt.hashpw(psw.encode(), bcrypt.gensalt()).decode()


def check_password(psw: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(psw.encode(), hashed_password.encode())
