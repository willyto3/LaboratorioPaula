from passlib.context import CryptContext

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hash:
    def bcrypt(password: str):
        return bcrypt_context.hash(password)

    def verify(plain_password, hash_password):
        return bcrypt_context.verify(plain_password, hash_password)
