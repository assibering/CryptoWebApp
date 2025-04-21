import uuid
import hashlib
import crypt

async def saltAndHashedPW(password: str):
    salt = crypt.mksalt(crypt.METHOD_SHA512)
    hashed_password = crypt.crypt(password, salt)
    return salt, hashed_password