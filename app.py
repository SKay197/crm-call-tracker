from flask import Flask, render_template, request, redirect, url_for, Response
from datetime import datetime
import sqlite3
import csv
import io

app = Flask(__name__)

DB_NAME = 'database.db'

# Initialize database
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS call_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            time_of_call TEXT,
            purpose TEXT,
            notes TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Fetch a single call log by ID
def get_call_by_id(call_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM call_logs WHERE id=?", (call_id,))
    call = c.fetchone()
    conn.close()
    return call

# Fetch filtered & searched calls
def search_calls(keyword=None, status=None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    query = "SELECT * FROM call_logs"
    filters = []
    params = []

    if keyword:
        filters.append("(name LIKE ? OR phone LIKE ?)")
        params.extend([f"%{keyword}%", f"%{keyword}%"])

    if status and status != "All":
        filters.append("status = ?")
        params.append(status)

    if filters:
        query += " WHERE " + " AND ".join(filters)

    query += " ORDER BY id DESC"
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return rows

# Fetch call counts by status
def get_dashboard_stats():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM call_logs")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM call_logs WHERE status='New'")
    new = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM call_logs WHERE status='Followed Up'")
    followed = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM call_logs WHERE status='Closed'")
    closed = c.fetchone()[0]
    conn.close()
    return {"total": total, "new": new, "followed": followed, "closed": closed}

# Home route with search + filter
@app.route('/')
def index():
    keyword = request.args.get('search')
    status = request.args.get('status')
    calls = search_calls(keyword, status)
    stats = get_dashboard_stats()
    return render_template('index.html', calls=calls, search=keyword or "", status_filter=status or "All", stats=stats)

# Add new call
@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    phone = request.form['phone']
    time_of_call = datetime.now().strftime('%Y-%m-%d %H:%M')
    purpose = request.form['purpose']
    notes = request.form['notes']
    status = 'New'

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO call_logs (name, phone, time_of_call, purpose, notes, status) VALUES (?, ?, ?, ?, ?, ?)",
              (name, phone, time_of_call, purpose, notes, status))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Update status only
@app.route('/update/<int:id>/<status>')
def update_status(id, status):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE call_logs SET status=? WHERE id=?", (status, id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Edit view
@app.route('/edit/<int:id>')
def edit_call(id):
    call = get_call_by_id(id)
    if not call:
        return "Call not found", 404
    return render_template('edit.html', call=call)

# Handle updates
@app.route('/update_call/<int:id>', methods=['POST'])
def update_call(id):
    name = request.form['name']
    phone = request.form['phone']
    purpose = request.form['purpose']
    notes = request.form['notes']
    status = request.form['status']

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        UPDATE call_logs
        SET name=?, phone=?, purpose=?, notes=?, status=?
        WHERE id=?
    ''', (name, phone, purpose, notes, status, id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Delete call
@app.route('/delete/<int:id>')
def delete_call(id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM call_logs WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Export to CSV
@app.route('/export')
def export_csv():
    keyword = request.args.get('search')
    status = request.args.get('status')
    calls = search_calls(keyword, status)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Phone', 'Time of Call', 'Purpose', 'Notes', 'Status'])

    for call in calls:
        writer.writerow(call)

    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=call_logs.csv"}
    )

# Run the app
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)

