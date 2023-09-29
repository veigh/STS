from base64 import b64encode, b64decode
from Crypto.Cipher.PKCS1_v1_5 import new
from Crypto.PublicKey.RSA import import_key
from Crypto.Random import get_random_bytes

from resources.paths import crt


class Cipher:
    def __init__(self, filename=crt):
        # Load from certificate in pem format
        with open(filename) as pem_file:
            self.cipher = new(import_key(pem_file.read()))

    # Encrypt value and encode it in base64
    def b64encrypt(self, value: str) -> str:
        return b64encode(self.encrypt(value)).decode('ascii')

    # Encrypt value
    def encrypt(self, value: str) -> bytes:
        return self.cipher.encrypt(value.encode('ascii'))

    def decrypt(self, value: bytes):
        return self.cipher.decrypt(value, get_random_bytes(16)).decode('ascii')

    def b64decrypt(self, value: str):
        return self.decrypt(b64decode(value.encode('ascii')))
