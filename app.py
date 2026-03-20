from flask import Flask, request, redirect
import sqlite3
import os

app = Flask(__name__)

DB = 'college.db'

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS students (
        student_id TEXT PRIMARY KEY,
        name TEXT,
        dob TEXT,
        gender TEXT,
        contact TEXT
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS courses (
        course_id TEXT PRIMARY KEY,
        course_name TEXT,
        credits INTEGER
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS grades (
        grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        course_id TEXT,
        marks INTEGER,
        grade TEXT,
        FOREIGN KEY (student_id) REFERENCES students(student_id),
        FOREIGN KEY (course_id) REFERENCES courses(course_id)
    )""")

    # Sample Data
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO students VALUES (?,?,?,?,?)", [
            ('S101', 'Rahul Sharma', '2002-05-10', 'Male', '9876543210'),
            ('S102', 'Priya Patel', '2003-01-15', 'Female', '9123456789'),
            ('S103', 'Amit Verma', '2002-08-20', 'Male', '9012345678')
        ])
        cursor.executemany("INSERT INTO courses VALUES (?,?,?)", [
            ('C01', 'Web Development', 4),
            ('C02', 'Data Structures', 3),
            ('C03', 'Database Management', 3),
            ('C04', 'Python Programming', 4)
        ])
        cursor.executemany("INSERT INTO grades (student_id, course_id, marks, grade) VALUES (?,?,?,?)", [
            ('S101', 'C01', 92, 'A'),
            ('S102', 'C02', 78, 'B'),
            ('S103', 'C03', 65, 'C')
        ])
    conn.commit()
    conn.close()

init_db()

def calculate_grade(marks):
    if marks >= 90: return 'A'
    elif marks >= 75: return 'B'
    elif marks >= 60: return 'C'
    elif marks >= 50: return 'D'
    else: return 'F'

STYLE = """
<style>
* { margin:0; padding:0; box-sizing:border-box; font-family:'Segoe UI',sans-serif; }
body { display:flex; background:#f0f4f8; }
.sidebar { width:220px; background:#1a73e8; height:100vh; padding:20px; position:fixed; }
.sidebar h2 { color:white; margin-bottom:30px; font-size:18px; }
.sidebar a { display:block; color:white; text-decoration:none; padding:12px 10px; border-radius:8px; margin-bottom:8px; }
.sidebar a:hover { background:#1558b0; }
.main { margin-left:240px; padding:30px; width:100%; }
h1 { color:#1a73e8; margin-bottom:25px; }
h2 { color:#1a73e8; margin-bottom:15px; }
.cards { display:flex; gap:20px; margin-bottom:30px; }
.card { background:white; padding:20px 30px; border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,0.1); flex:1; text-align:center; border-top:4px solid #1a73e8; }
.card h3 { color:#555; font-size:14px; margin-bottom:10px; }
.card p { color:#1a73e8; font-size:28px; font-weight:bold; }
table { width:100%; border-collapse:collapse; background:white; border-radius:12px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.1); margin-bottom:25px; }
thead { background:#1a73e8; color:white; }
th, td { padding:14px 18px; text-align:left; font-size:14px; }
tr:nth-child(even) { background:#f0f4f8; }
tr:hover { background:#d0e4ff; }
.form-box { background:white; padding:20px; border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,0.1); margin-bottom:25px; }
.form-box input, .form-box select { padding:10px; border-radius:6px; border:1px solid #ccc; margin:5px; width:200px; }
.btn { padding:10px 20px; border:none; border-radius:6px; cursor:pointer; color:white; margin:5px; }
.btn-add { background:#1a73e8; }
.btn-del { background:#ea4335; }
</style>
"""

SIDEBAR = """
<div class="sidebar">
    <h2>🎓 RTMNU College</h2>
    <a href="/">📊 Dashboard</a>
    <a href="/students">👨‍🎓 Students</a>
    <a href="/courses">📚 Courses</a>
    <a href="/grades">📝 Grades</a>
</div>
"""

@app.route('/')
def dashboard():
    conn = get_db()
    students = conn.execute("SELECT * FROM students").fetchall()
    ts = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    tc = conn.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
    tg = conn.execute("SELECT COUNT(*) FROM grades").fetchone()[0]
    conn.close()
    rows = "".join(f"<tr><td>{s['student_id']}</td><td>{s['name']}</td><td>{s['gender']}</td><td>{s['contact']}</td></tr>" for s in students)
    return f"""<!DOCTYPE html><html><head><title>Dashboard</title>{STYLE}</head><body>
    {SIDEBAR}
    <div class="main">
        <h1>Enrollment & Grade Management System</h1>
        <div class="cards">
            <div class="card"><h3>Total Students</h3><p>{ts}</p></div>
            <div class="card"><h3>Active Courses</h3><p>{tc}</p></div>
            <div class="card"><h3>Total Grades</h3><p>{tg}</p></div>
        </div>
        <h2>Recent Students</h2>
        <table><thead><tr><th>ID</th><th>Name</th><th>Gender</th><th>Contact</th></tr></thead>
        <tbody>{rows}</tbody></table>
    </div></body></html>"""

@app.route('/students')
def students():
    conn = get_db()
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    rows = "".join(f"<tr><td>{s['student_id']}</td><td>{s['name']}</td><td>{s['dob']}</td><td>{s['gender']}</td><td>{s['contact']}</td><td><a href='/delete_student/{s['student_id']}'><button class='btn btn-del'>🗑️ Delete</button></a></td></tr>" for s in students)
    return f"""<!DOCTYPE html><html><head><title>Students</title>{STYLE}</head><body>
    {SIDEBAR}
    <div class="main">
        <h1>Student Management</h1>
        <div class="form-box">
            <h2>➕ Add Student</h2>
            <form action="/add_student" method="POST">
                <input type="text" name="student_id" placeholder="Student ID" required>
                <input type="text" name="name" placeholder="Full Name" required>
                <input type="date" name="dob">
                <select name="gender">
                    <option>Male</option>
                    <option>Female</option>
                    <option>Other</option>
                </select>
                <input type="text" name="contact" placeholder="Contact">
                <button type="submit" class="btn btn-add">Add Student</button>
            </form>
        </div>
        <h2>All Students</h2>
        <table><thead><tr><th>ID</th><th>Name</th><th>DOB</th><th>Gender</th><th>Contact</th><th>Action</th></tr></thead>
        <tbody>{rows}</tbody></table>
    </div></body></html>"""

@app.route('/add_student', methods=['POST'])
def add_student():
    conn = get_db()
    conn.execute("INSERT INTO students VALUES (?,?,?,?,?)",
        (request.form['student_id'], request.form['name'],
         request.form['dob'], request.form['gender'], request.form['contact']))
    conn.commit()
    conn.close()
    return redirect('/students')

@app.route('/delete_student/<sid>')
def delete_student(sid):
    conn = get_db()
    conn.execute("DELETE FROM grades WHERE student_id=?", (sid,))
    conn.execute("DELETE FROM students WHERE student_id=?", (sid,))
    conn.commit()
    conn.close()
    return redirect('/students')

@app.route('/courses')
def courses():
    conn = get_db()
    courses = conn.execute("SELECT * FROM courses").fetchall()
    conn.close()
    rows = "".join(f"<tr><td>{c['course_id']}</td><td>{c['course_name']}</td><td>{c['credits']}</td><td><a href='/delete_course/{c['course_id']}'><button class='btn btn-del'>🗑️ Delete</button></a></td></tr>" for c in courses)
    return f"""<!DOCTYPE html><html><head><title>Courses</title>{STYLE}</head><body>
    {SIDEBAR}
    <div class="main">
        <h1>Course Management</h1>
        <div class="form-box">
            <h2>➕ Add Course</h2>
            <form action="/add_course" method="POST">
                <input type="text" name="course_id" placeholder="Course ID" required>
                <input type="text" name="course_name" placeholder="Course Name" required>
                <input type="number" name="credits" placeholder="Credits" min="1" max="6" required>
                <button type="submit" class="btn btn-add">Add Course</button>
            </form>
        </div>
        <h2>All Courses</h2>
        <table><thead><tr><th>ID</th><th>Course Name</th><th>Credits</th><th>Action</th></tr></thead>
        <tbody>{rows}</tbody></table>
    </div></body></html>"""

@app.route('/add_course', methods=['POST'])
def add_course():
    conn = get_db()
    conn.execute("INSERT INTO courses VALUES (?,?,?)",
        (request.form['course_id'], request.form['course_name'], request.form['credits']))
    conn.commit()
    conn.close()
    return redirect('/courses')

@app.route('/delete_course/<cid>')
def delete_course(cid):
    conn = get_db()
    conn.execute("DELETE FROM grades WHERE course_id=?", (cid,))
    conn.execute("DELETE FROM courses WHERE course_id=?", (cid,))
    conn.commit()
    conn.close()
    return redirect('/courses')

@app.route('/grades')
def grades():
    conn = get_db()
    grades = conn.execute("""
        SELECT g.grade_id, s.name, c.course_name, g.marks, g.grade
        FROM grades g
        JOIN students s ON g.student_id = s.student_id
        JOIN courses c ON g.course_id = c.course_id
    """).fetchall()
    students = conn.execute("SELECT * FROM students").fetchall()
    courses = conn.execute("SELECT * FROM courses").fetchall()
    conn.close()
    grade_rows = "".join(f"<tr><td>{g['grade_id']}</td><td>{g['name']}</td><td>{g['course_name']}</td><td>{g['marks']}</td><td>{g['grade']}</td><td><a href='/delete_grade/{g['grade_id']}'><button class='btn btn-del'>🗑️ Delete</button></a></td></tr>" for g in grades)
    student_options = "".join(f"<option value='{s['student_id']}'>{s['student_id']} - {s['name']}</option>" for s in students)
    course_options = "".join(f"<option value='{c['course_id']}'>{c['course_id']} - {c['course_name']}</option>" for c in courses)
    return f"""<!DOCTYPE html><html><head><title>Grades</title>{STYLE}</head><body>
    {SIDEBAR}
    <div class="main">
        <h1>Grade Management</h1>
        <div class="form-box">
            <h2>➕ Add Marks</h2>
            <form action="/add_grade" method="POST">
                <select name="student_id" required>{student_options}</select>
                <select name="course_id" required>{course_options}</select>
                <input type="number" name="marks" placeholder="Marks (0-100)" min="0" max="100" required>
                <button type="submit" class="btn btn-add">Add Grade</button>
            </form>
        </div>
        <h2>All Grades</h2>
        <table><thead><tr><th>ID</th><th>Student</th><th>Course</th><th>Marks</th><th>Grade</th><th>Action</th></tr></thead>
        <tbody>{grade_rows}</tbody></table>
    </div></body></html>"""

@app.route('/add_grade', methods=['POST'])
def add_grade():
    marks = int(request.form['marks'])
    conn = get_db()
    conn.execute("INSERT INTO grades (student_id, course_id, marks, grade) VALUES (?,?,?,?)",
        (request.form['student_id'], request.form['course_id'], marks, calculate_grade(marks)))
    conn.commit()
    conn.close()
    return redirect('/grades')

@app.route('/delete_grade/<int:gid>')
def delete_grade(gid):
    conn = get_db()
    conn.execute("DELETE FROM grades WHERE grade_id=?", (gid,))
    conn.commit()
    conn.close()
    return redirect('/grades')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)