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
    c.execute('''CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, email TEXT NOT NULL,
        message TEXT NOT NULL, received_at TEXT NOT NULL)''')
    conn.commit()
    conn.close()

ADMIN_PASSWORD = "harshilhax2025"

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    name = data.get('name','').strip()
    email = data.get('email','').strip()
    message = data.get('message','').strip()
    if not name or not email or not message:
        return jsonify({'success': False}), 400
    conn = sqlite3.connect('contacts.db')
    c = conn.cursor()
    c.execute('INSERT INTO contacts (name,email,message,received_at) VALUES (?,?,?,?)',
        (name, email, message, datetime.datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d-%m-%Y %I:%M %p")))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/admin')
def admin():
    password = request.args.get('password','')
    if password != ADMIN_PASSWORD:
        return '''<form style="font-family:sans-serif;max-width:300px;margin:100px auto;display:grid;gap:12px">
          <h2>Admin Login</h2>
          <input name="password" type="password" placeholder="Password"
            style="padding:10px;border-radius:8px;border:1px solid #ccc">
          <button type="submit"
            style="padding:10px;background:#19ffd2;border:none;border-radius:8px;cursor:pointer;font-weight:700">
            Login</button></form>'''
    conn = sqlite3.connect('contacts.db')
    c = conn.cursor()
    c.execute('SELECT * FROM contacts ORDER BY received_at DESC')
    rows = c.fetchall()
    conn.close()
    rows_html = ''
    for row in rows:
        rows_html += f'''<tr>
          <td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td>
          <td>{row[3]}</td><td>{row[4]}</td>
          <td><a href="/delete/{row[0]}?password={password}"
            onclick="return confirm('Delete?')"
            style="color:#ff6b6b;font-weight:700;text-decoration:none">Delete</a></td></tr>'''
    return f'''<!DOCTYPE html><html><head><title>Admin | Harshil HAX</title>
    <style>body{{font-family:Inter,sans-serif;background:#050b10;color:#eafffb;padding:40px}}
    h2{{color:#19ffd2;margin-bottom:20px}}table{{width:100%;border-collapse:collapse}}
    th{{background:#0b141b;color:#19ffd2;padding:12px;text-align:left}}
    td{{padding:12px;border-bottom:1px solid rgba(255,255,255,0.08)}}
    tr:hover td{{background:rgba(25,255,210,0.05)}}</style></head>
    <body><h2>Contact Messages</h2>
    <p style="color:#8fb3ad;margin-bottom:20px">Total: {len(rows)} messages</p>
    <table><tr><th>ID</th><th>Name</th><th>Email</th>
    <th>Message</th><th>Time (IST)</th><th>Action</th></tr>
    {rows_html}</table></body></html>'''

@app.route('/delete/<int:msg_id>')
def delete(msg_id):
    password = request.args.get('password','')
    if password != ADMIN_PASSWORD:
        return 'Unauthorized', 401
    conn = sqlite3.connect('contacts.db')
    c = conn.cursor()
    c.execute('DELETE FROM contacts WHERE id = ?', (msg_id,))
    conn.commit()
    conn.close()
    return f'<script>window.location="/admin?password={password}"</script>'

if __name__ == '__main__':
    init_db()
    app.run(debug=True)