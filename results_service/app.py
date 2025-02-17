from flask import Flask, render_template, redirect, url_for, session, request
from pymongo import MongoClient
import requests
from functools import wraps
import os
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')

# MongoDB configuration
mongo_client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
mongo_db = mongo_client['analytics_db']
mongo_collection = mongo_db['analytics']

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'token' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        response = requests.post('http://auth_service:5000/login', json={
            'username': request.form['username'],
            'password': request.form['password']
        })
        
        if response.status_code == 200:
            session['token'] = response.json()['token']
            return redirect(url_for('results'))
        return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/results')
@login_required
def results():
    # Get the latest analytics from MongoDB
    analytics = mongo_collection.find_one(
        sort=[('timestamp', -1)]
    )
    
    return render_template('results.html', analytics=analytics)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)