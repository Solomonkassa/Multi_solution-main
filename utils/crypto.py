import base64
import secrets
import time
import hmac
from hashlib import sha256

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from django.conf import settings

def hash256(msg: str) -> str:
    return sha256(msg.encode()).hexdigest()

def gen_api_key():
    return AESEncryption.get_new_key()

class AESEncryption:
    @staticmethod
    def encrypt(plaintext, key=settings.ENCRYPTION_KEY):
        t1 = time.time()
        plaintext = plaintext.encode("utf-8")
        key = base64.b64decode(key.encode())
        key = bytes.fromhex(key.decode())
        cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
        encryptor = cipher.encryptor()
        padder = PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(plaintext) + padder.finalize()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        encoded_ciphertext = base64.b64encode(ciphertext)
        t2 = time.time()
        print("Encryption time:", t2 - t1)
        return encoded_ciphertext

    @staticmethod
    def decrypt(ciphertext, key=settings.ENCRYPTION_KEY):
        key = base64.b64decode(key.encode())
        key = bytes.fromhex(key.decode())
        cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
        decryptor = cipher.decryptor()
        decoded_ciphertext = base64.b64decode(ciphertext)
        padded_data = decryptor.update(decoded_ciphertext) + decryptor.finalize()
        unpadder = PKCS7(algorithms.AES.block_size).unpadder()
        plaintext = unpadder.update(padded_data) + unpadder.finalize()
        return plaintext.decode()

    @staticmethod
    def get_new_key(length=32):
        token = secrets.token_hex(length)
        token = base64.b64encode(token.encode())
        return token.decode()

class RSAEncryption:
    @staticmethod
    def sign(message: str, private_key_path: str) -> str:
        private_key = None
        with open(private_key_path, "rb") as f:
            private_key = load_pem_private_key(f.read(), None)

        message = message.encode()
        signature = private_key.sign(
            message,
            PKCS1v15(),
            hashes.SHA256(),
        )
        return base64.b64encode(signature).decode()

    @staticmethod
    def verify(message: str, signature: str, public_key_path: str) -> bool:
        try:
            public_key = None
            signature = base64.b64decode(signature)
            message = message.encode()
            with open(public_key_path, "rb") as f:
                public_key = load_pem_public_key(f.read())
            public_key.verify(
                signature,
                message,
                PKCS1v15(),
                hashes.SHA256(),
            )
            return True
        except Exception as e:
            return False

    @staticmethod
    def gen_keys():
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )
        public_key = private_key.public_key()

        private_key_pem = private_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NoEncryption(),
        )

        public_key_pem = public_key.public_bytes(
            encoding=Encoding.PEM, format=PublicFormat.SubjectPublicKeyInfo
        )

        return private_key_pem, public_key_pem

def hmac_sha256(msg):
    secret = settings.CHAPA_HOOK_HASH
    secret_key_bytes = secret.encode("utf-8")
    message_bytes = msg.encode("utf-8")
    hmacsha256 = hmac.new(secret_key_bytes, message_bytes, sha256)
    digest = hmacsha256.digest()
    hex_digest = hmacsha256.hexdigest()
    print("HMAC-SHA256 Digest (bytes):", digest)
    print("HMAC-SHA256 Digest (hex):", hex_digest)
    return hex_digest

