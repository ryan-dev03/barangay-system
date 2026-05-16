from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'barangay_secret'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'brgy_user'
app.config['MYSQL_PASSWORD'] = 'gchbarangay'
app.config['MYSQL_DB'] = 'barangay_db'

mysql = MySQL(app)

@app.route('/')
def index():
    return redirect(url_for('admin_login'))

# MEMBER

@app.route('/unit/<unit_number>')
def unit_entry(unit_number):
    return redirect(url_for('member_login', unit=unit_number))

@app.route('/login/<unit>', methods=['GET', 'POST'])
def member_login(unit):
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM members WHERE username=%s", (username,))
        member = cur.fetchone()

        if member and check_password_hash(member[4], password):
            session['member_id'] = member[0]
            session['unit'] = unit
            return redirect(url_for('member_home'))

        return render_template('member/login.html', unit=unit, error='Invalid credentials')

    return render_template('member/login.html', unit=unit)

@app.route('/register/<unit>', methods=['GET','POST'])
def register(unit):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM house_units WHERE unit_number=%s", (unit,))
    house = cur.fetchone()

    if not house:
        return "Invalid house unit.", 404

    if request.method == 'POST':
        full_name = request.form['full_name']
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']

        if password != confirm:
            return render_template('member/register.html', unit=unit, error='Passwords do not match.')

        cur.execute("SELECT * FROM members WHERE username=%s", (username,))
        if cur.fetchone():
            return render_template('member/register.html', unit=unit, error='Username already taken.')

        password_hash = generate_password_hash(password)

        cur.execute("""
            INSERT INTO members (house_unit_id, full_name, username, password_hash)
            VALUES (%s,%s,%s,%s)
        """, (house[0], full_name, username, password_hash))

        mysql.connection.commit()
        return redirect(url_for('member_login', unit=unit))

    return render_template('member/register.html', unit=unit)

@app.route('/home')
def member_home():
    if 'member_id' not in session:
        return redirect('/')
    return render_template('member/home.html')

@app.route('/request-file', methods=['GET','POST'])
def request_file():
    if 'member_id' not in session:
        return redirect('/')

    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO file_requests (member_id,file_type,details,delivery_address)
            VALUES (%s,%s,%s,%s)
        """, (
            session['member_id'],
            request.form['file_type'],
            request.form.get('details',''),
            request.form['delivery_address']
        ))
        mysql.connection.commit()
        return redirect(url_for('member_home'))

    return render_template('member/request_file.html')

@app.route('/complaint', methods=['GET','POST'])
def complaint():
    if 'member_id' not in session:
        return redirect('/')

    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO complaints (member_id,complaint_type,description)
            VALUES (%s,%s,%s)
        """, (
            session['member_id'],
            request.form['complaint_type'],
            request.form['description']
        ))
        mysql.connection.commit()
        return redirect(url_for('member_home'))

    return render_template('member/complaint.html')

@app.route('/emergency', methods=['GET','POST'])
def emergency():
    if 'member_id' not in session:
        return redirect('/')

    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO emergencies (member_id,emergency_type,description,location,contact_number)
            VALUES (%s,%s,%s,%s,%s)
        """, (
            session['member_id'],
            request.form['emergency_type'],
            request.form.get('description',''),
            request.form['location'],
            request.form.get('contact','')
        ))
        mysql.connection.commit()
        return redirect(url_for('member_home'))

    return render_template('member/emergency.html')

# ADMIN

@app.route('/admin', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM admins WHERE username=%s", (request.form['username'],))
        admin = cur.fetchone()

        if admin and request.form['password'] == admin[2]:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))

        return render_template('admin/login.html', error='Invalid credentials')

    return render_template('admin/login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT fr.id, fr.file_type, fr.details, fr.delivery_address,
               fr.status, fr.created_at, m.full_name, h.unit_number, h.id
        FROM file_requests fr
        JOIN members m ON fr.member_id=m.id
        JOIN house_units h ON m.house_unit_id=h.id
        ORDER BY h.unit_number, fr.created_at DESC
    """)
    requests = cur.fetchall()

    cur.execute("""
        SELECT c.id, c.complaint_type, c.description, c.status,
               c.created_at, m.full_name, h.unit_number, h.id
        FROM complaints c
        JOIN members m ON c.member_id=m.id
        JOIN house_units h ON m.house_unit_id=h.id
        ORDER BY h.unit_number, c.created_at DESC
    """)
    complaints = cur.fetchall()

    cur.execute("""
        SELECT e.id, e.emergency_type, e.description, e.location,
               e.contact_number, e.status, e.created_at, m.full_name,
               h.unit_number, h.id
        FROM emergencies e
        JOIN members m ON e.member_id=m.id
        JOIN house_units h ON m.house_unit_id=h.id
        ORDER BY e.created_at DESC
    """)
    emergencies = cur.fetchall()

    cur.execute("SELECT * FROM house_units ORDER BY unit_number")
    house_units = cur.fetchall()

    # GROUPING
    grouped_requests = defaultdict(list)
    for r in requests:
        grouped_requests[r[7]].append(r)

    grouped_complaints = defaultdict(list)
    for c in complaints:
        grouped_complaints[c[6]].append(c)

    grouped_emergencies = defaultdict(list)
    for e in emergencies:
        grouped_emergencies[e[8]].append(e)

    return render_template(
        'admin/dashboard.html',
        house_units=house_units,
        grouped_requests=grouped_requests,
        grouped_complaints=grouped_complaints,
        grouped_emergencies=grouped_emergencies
    )

@app.route('/admin/update-status', methods=['POST'])
def update_status():
    cur = mysql.connection.cursor()
    cur.execute(f"UPDATE {request.form['table']} SET status=%s WHERE id=%s",
                (request.form['status'], request.form['record_id']))
    mysql.connection.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/qrcodes')
def qrcodes():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    return render_template('admin/qrcodes.html')

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/logout')
def member_logout():
    unit = session.get('unit') 
    session.clear() 
    if unit:
        return redirect(url_for('member_login', unit=unit))
    return redirect('/') 


#  MEMBER SUBMISSIONS

@app.route('/member/my-submissions')
def my_submissions():
    if 'member_id' not in session:
        return redirect('/')

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 'File Request', file_type, status, created_at FROM file_requests WHERE member_id=%s
        UNION ALL
        SELECT 'Complaint', complaint_type, status, created_at FROM complaints WHERE member_id=%s
        UNION ALL
        SELECT 'Emergency', emergency_type, status, created_at FROM emergencies WHERE member_id=%s
        ORDER BY created_at DESC
    """, (session['member_id'],)*3)

    return render_template('member/my_submissions.html', submissions=cur.fetchall())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
