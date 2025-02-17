from flask import Flask
import mysql.connector
from pymongo import MongoClient
import schedule
import time
import os
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Database configurations
mysql_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'password'),
    'database': os.getenv('MYSQL_DATABASE', 'data_entry_db')
}

mongo_client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
mongo_db = mongo_client['analytics_db']
mongo_collection = mongo_db['analytics']

def calculate_analytics():
    # Connect to MySQL
    mysql_conn = mysql.connector.connect(**mysql_config)
    cursor = mysql_conn.cursor()
    
    # Get analytics
    cursor.execute("""
        SELECT 
            MAX(value) as max_value,
            MIN(value) as min_value,
            AVG(value) as avg_value,
            COUNT(*) as count
        FROM data
    """)
    
    result = cursor.fetchone()
    
    # Store in MongoDB
    analytics = {
        'max_value': result[0],
        'min_value': result[1],
        'avg_value': float(result[2]) if result[2] else 0,
        'count': result[3],
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    mongo_collection.insert_one(analytics)
    
    cursor.close()
    mysql_conn.close()

def init_scheduler():
    schedule.every(5).minutes.do(calculate_analytics)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    # Run the scheduler in a separate thread
    import threading
    scheduler_thread = threading.Thread(target=init_scheduler)
    scheduler_thread.start()
    
    app.run(host='0.0.0.0', port=5002)