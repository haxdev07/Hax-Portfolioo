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
        return '''<!DOCTYPE html><html><head><title>Admin Login</title>
        <style>
          body{font-family:Inter,sans-serif;background:#050b10;color:#eafffb;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}
          .box{background:#0b141b;padding:40px;border-radius:16px;border:1px solid rgba(255,255,255,.08);width:300px}
          h2{color:#19ffd2;margin-bottom:24px;text-align:center}
          input{width:100%;padding:12px;border-radius:10px;border:1px solid rgba(255,255,255,.15);background:transparent;color:#eafffb;box-sizing:border-box;margin-bottom:16px;font-size:15px}
          button{width:100%;padding:12px;background:#19ffd2;border:none;border-radius:10px;cursor:pointer;font-weight:700;font-size:15px;color:#00130f}
        </style></head>
        <body><div class="box">
          <h2>Admin Login</h2>
          <form>
            <input name="password" type="password" placeholder="Enter password">
            <button type="submit">Login</button>
          </form>
        </div></body></html>'''

    conn = sqlite3.connect('contacts.db')
    c = conn.cursor()
    c.execute('SELECT * FROM contacts ORDER BY received_at DESC')
    rows = c.fetchall()
    conn.close()

    # Renumber rows for display (1, 2, 3... regardless of DB id)
    rows_html = ''
    for i, row in enumerate(rows, 1):
        rows_html += f'''
        <tr id="row-{row[0]}">
          <td style="color:#8fb3ad">{i}</td>
          <td><strong>{row[1]}</strong></td>
          <td><a href="mailto:{row[2]}" style="color:#19ffd2">{row[2]}</a></td>
          <td style="max-width:300px">{row[3]}</td>
          <td style="color:#8fb3ad;white-space:nowrap">{row[4]}</td>
          <td>
            <button onclick="copyMsg({row[0]}, '{row[1]}', '{row[2]}', `{row[3]}`)"
              style="background:rgba(25,255,210,0.15);color:#19ffd2;border:1px solid rgba(25,255,210,0.3);padding:6px 12px;border-radius:8px;cursor:pointer;font-size:12px;margin-bottom:6px;width:100%">
              Copy
            </button>
            <button onclick="deleteMsg({row[0]}, this)"
              style="background:rgba(255,80,80,0.15);color:#ff6b6b;border:1px solid rgba(255,80,80,0.3);padding:6px 12px;border-radius:8px;cursor:pointer;font-size:12px;width:100%">
              Delete
            </button>
          </td>
        </tr>'''

    return f'''<!DOCTYPE html>
    <html><head>
    <title>Admin | Harshil HAX</title>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <style>
      *{{box-sizing:border-box;margin:0;padding:0}}
      body{{font-family:Inter,sans-serif;background:#050b10;color:#eafffb;padding:40px 24px}}
      h2{{color:#19ffd2;margin-bottom:6px;font-size:24px}}
      .meta{{color:#8fb3ad;margin-bottom:28px;font-size:14px}}
      table{{width:100%;border-collapse:collapse;font-size:14px}}
      th{{background:#0b141b;color:#19ffd2;padding:14px 12px;text-align:left;border-bottom:1px solid rgba(255,255,255,.08)}}
      td{{padding:14px 12px;border-bottom:1px solid rgba(255,255,255,.05);vertical-align:top}}
      tr:hover td{{background:rgba(25,255,210,0.03)}}
      .toast{{position:fixed;bottom:24px;right:24px;background:#19ffd2;color:#00130f;padding:12px 20px;border-radius:10px;font-weight:700;font-size:14px;display:none;z-index:999}}
    </style>
    </head>
    <body>
      <h2>Contact Messages</h2>
      <p class="meta">Total: {len(rows)} messages &nbsp;|&nbsp; Password protected</p>

      <table>
        <tr>
          <th>#</th>
          <th>Name</th>
          <th>Email</th>
          <th>Message</th>
          <th>Time (IST)</th>
          <th style="width:100px">Actions</th>
        </tr>
        {rows_html if rows_html else '<tr><td colspan="6" style="text-align:center;padding:40px;color:#8fb3ad">No messages yet</td></tr>'}
      </table>

      <div class="toast" id="toast">Copied!</div>

    <script>
    const PASSWORD = '{password}';

    function copyMsg(id, name, email, message) {{
      const text = `Name: ${{name}}\\nEmail: ${{email}}\\nMessage: ${{message}}`;
      navigator.clipboard.writeText(text).then(() => {{
        const toast = document.getElementById('toast');
        toast.style.display = 'block';
        setTimeout(() => toast.style.display = 'none', 2000);
      }});
    }}

    function deleteMsg(id, btn) {{
      if (!confirm('Delete this message?')) return;
      btn.textContent = '...';
      btn.disabled = true;
      fetch(`/delete/${{id}}?password=${{PASSWORD}}`)
        .then(res => res.json())
        .then(data => {{
          if (data.success) {{
            document.getElementById('row-' + id).remove();
            // Renumber all rows
            document.querySelectorAll('table tr[id]').forEach((row, i) => {{
              row.querySelector('td').textContent = i + 1;
            }});
            // Update total count
            const remaining = document.querySelectorAll('table tr[id]').length;
            document.querySelector('.meta').textContent = `Total: ${{remaining}} messages | Password protected`;
          }}
        }});
    }}
    </script>
    </body></html>'''

@app.route('/delete/<int:msg_id>')
def delete(msg_id):
    password = request.args.get('password','')
    if password != ADMIN_PASSWORD:
        return jsonify({'success': False}), 401
    conn = sqlite3.connect('contacts.db')
    c = conn.cursor()
    c.execute('DELETE FROM contacts WHERE id = ?', (msg_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)