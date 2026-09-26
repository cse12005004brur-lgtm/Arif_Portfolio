import os
import psycopg2
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ.get('DB_HOST', 'db'),
        database=os.environ.get('DB_NAME', 'myappdb'),
        user=os.environ.get('DB_USER', 'myuser'),
        password=os.environ.get('DB_PASSWORD', 'mypassword'),
        port=os.environ.get('DB_PORT', 5432)
    )
    return conn

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL
            );
        ''')
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Database initialization error: {e}")

@app.route('/')
def home():
    init_db()
    return render_template('index.html')

@app.route('/items', methods=['GET', 'POST'])
def handle_items():
    init_db()
    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == 'POST':
        data = request.get_json() or {}
        name = data.get('name', 'Sample Item')
        cur.execute('INSERT INTO items (name) VALUES (%s) RETURNING id, name;', (name,))
        inserted_item = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'id': inserted_item[0], 'name': inserted_item[1]}), 201
    
    cur.execute('SELECT id, name FROM items;')
    items = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{'id': item[0], 'name': item[1]} for item in items])

if __name__ == '__main__':
    app.run(debug=True)