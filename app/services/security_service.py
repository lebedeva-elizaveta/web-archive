import base64
from base64 import urlsafe_b64encode

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes


class EncryptionService:

    @staticmethod
    def generate_password_hash(password):
        password_bytes = password.encode('utf-8')
        algorithm = hashes.SHA256()
        digest = hashes.Hash(algorithm, backend=default_backend())
        digest.update(password_bytes)
        hashed_password = digest.finalize()
        hashed_password_b64 = urlsafe_b64encode(hashed_password).rstrip(b'=').decode('utf-8')
        return hashed_password_b64

    @staticmethod
    def check_password(hashed_password, password):
        password_bytes = password.encode('utf-8')
        hashed_password_bytes = base64.urlsafe_b64decode(hashed_password.encode('utf-8') + b'=')
        algorithm = hashes.SHA256()
        digest = hashes.Hash(algorithm, backend=default_backend())
        digest.update(password_bytes)
        hashed_input_password = digest.finalize()
        return hashed_password_bytes == hashed_input_password
