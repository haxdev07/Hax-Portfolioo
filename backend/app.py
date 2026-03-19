from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import datetime
from zoneinfo import ZoneInfo

app = Flask(__name__)
CORS(app, origins="*")

def init_db():
    conn = sqlite3.connect('contacts.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            received_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    name    = data.get('name', '').strip()
    email   = data.get('email', '').strip()
    message = data.get('message', '').strip()

    if not name or not email or not message:
        return jsonify({'success': False, 'error': 'All fields required'}), 400

    conn = sqlite3.connect('contacts.db')
    c = conn.cursor()
    c.execute(
        'INSERT INTO contacts (name, email, message, received_at) VALUES (?, ?, ?, ?)',
        (name, email, message, datetime.datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

    print(f"New message from {name} ({email})")
    return jsonify({'success': True})

@app.route('/messages')
def messages():
    conn = sqlite3.connect('contacts.db')
    c = conn.cursor()
    c.execute('SELECT * FROM contacts ORDER BY received_at DESC')
    rows = c.fetchall()
    conn.close()

    html = '<h2>Contact Messages</h2><table border="1" cellpadding="8">'
    html += '<tr><th>ID</th><th>Name</th><th>Email</th><th>Message</th><th>Time</th></tr>'
    for row in rows:
        html += f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td></tr>'
    html += '</table>'
    return html

if __name__ == '__main__':
    init_db()
    app.run(debug=True)