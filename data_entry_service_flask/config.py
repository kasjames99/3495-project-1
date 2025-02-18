import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'password')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'data_entry_db')
    AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://auth_service:5000')