from passlib.hash import sha512_crypt

async def saltAndHashedPW(password: str):
    # Generate a random salt and hash the password
    # passlib handles salt generation internally
    return sha512_crypt.hash(password)