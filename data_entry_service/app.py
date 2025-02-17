from flask import Flask, request, render_template, redirect, url_for, session
import requests
import mysql.connector
from functools import wraps
import os
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')

# Database configuration
db_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'password'),
    'database': os.getenv('MYSQL_DATABASE', 'data_entry_db')
}

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
            return redirect(url_for('data_entry'))
        return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/data_entry', methods=['GET', 'POST'])
@login_required
def data_entry():
    if request.method == 'POST':
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO data (value, timestamp)
            VALUES (%s, NOW())
        """, (request.form['value'],))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('data_entry'))
    
    return render_template('data_entry.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)