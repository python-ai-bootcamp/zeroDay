import os,tarfile
from systemEntities import print
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_ssh_public_key, load_ssh_private_key
from cryptography.fernet import Fernet
from fastapi.responses import PlainTextResponse


DATA_DIR = os.path.join("./data")
DATA_DIR_ARCHIVE_FILE=os.path.join(DATA_DIR,"data.tar.gz")
NEW_SYMMETRIC_KEY=""
public_key = load_ssh_public_key(open(os.path.join("resources","keys","id_rsa.pub"), "r").read().encode("utf-8"))


def encrypt_symmetric_key_by_public_key(message: str):
    ciphertext = public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext

def fetch_symmetric_key():
    global NEW_SYMMETRIC_KEY 
    NEW_SYMMETRIC_KEY = Fernet.generate_key()
    return PlainTextResponse(encrypt_symmetric_key_by_public_key(NEW_SYMMETRIC_KEY))

def download_data():
    with tarfile.open(DATA_DIR_ARCHIVE_FILE, mode='w:gz') as archive:
        archive.add(DATA_DIR, recursive=True)
    with open(DATA_DIR_ARCHIVE_FILE, "rb") as f:
        archived_data=f.read()
    sym_key=Fernet(NEW_SYMMETRIC_KEY)
    encrypted_content=sym_key.encrypt(archived_data)
    return PlainTextResponse(encrypted_content)