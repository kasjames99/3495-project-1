import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'password')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'data_entry_db')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    ANALYTICS_UPDATE_INTERVAL = int(os.getenv('ANALYTICS_UPDATE_INTERVAL', '300'))