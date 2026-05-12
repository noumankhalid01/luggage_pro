import firebase_admin
from firebase_admin import credentials
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "firebase_service_account.json")

def init_firebase():
    if firebase_admin._apps:
        print("Firebase already initialized.")
        return firebase_admin.get_app()

    cred = credentials.Certificate(CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)
    print("Firebase initialized successfully.")
