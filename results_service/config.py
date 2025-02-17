import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://auth_service:5000')
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'analytics_db')
    MONGO_COLLECTION_NAME = os.getenv('MONGO_COLLECTION_NAME', 'analytics')