from flask import Flask, render_template, request, redirect
from flask import session, g, url_for, flash
import sqlite3
import os
import re

app = Flask(__name__)
status_msg = " "
# run and create database

@app.route('/')
def index():
    return redirect("/login")

@app.route('/login', methods=['GET','POST'])
def login():
    global status_msg
    if request.method == "POST":
        if request.form['username'] == 'root' and request.form['password'] == 'toor':
            session['logged_in'] = True
            session['username'] = request.form['username']
            return redirect('/dashboard')
        else:
            status_msg = 'Username & Password is Invalid'

    return render_template('login.html', status_msg=status_msg)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    global status_msg

    if 'logged_in' not in session:
        return redirect ('/login')
    con = sqlite3.connect('hw13.db')
    student_list = con.execute("SELECT * FROM Students ORDER BY id ASC")

    Students = [
        dict(id= row[0], first_name=row[1], last_name=row[2])
        for row in student_list.fetchall()
        ]
    quiz_list = con.execute("SELECT * FROM Quiz ORDER BY id ASC")

    Quiz = [
        dict(id= row[0], subject=row[1], questions=row[2], quiz_date=row[3])
        for row in quiz_list.fetchall()
        ]
    con.commit()
    con.close()
    return render_template('dashboard.html', roaster=Students, quiz_data = Quiz)

# Adding Student
@app.route('/student_add', methods=['GET', 'POST'])
def student_add():
    if 'logged_in' not in session:
        return redirect('/login')

    global status_msg
    n_fname = ""
    n_lname = ""
    if not ('fname' in request.form and 'lname' in request.form):
        status_msg = ""
        return render_template('student_add.html',status_msg=status_msg)
    elif 'fname' in request.form and 'lname' in request.form:
        n_fname = request.form['fname']
        n_lname = request.form['lname']
    else:
        status_msg = "Please fill the form completly"
        return render_template('student_add.html',status_msg=status_msg)
    con = sqlite3.connect("hw13.db")
    query = '''INSERT INTO Students (fname, lname)
                    VALUES ("%s", "%s");''' % (n_fname, n_lname)
    con.execute(query)
    con.commit()
    con.close()
    return redirect('/dashboard')

#Adding Quiz
@app.route('/quiz_add', methods=['GET', 'POST'])
def quiz_add():
    if 'logged_in' not in session:
        return redirect('/login')

    global status_msg
    n_sub = ""
    n_question = ""
    n_date = ""
    if not ('subject' in request.form and 'question' in request.form and 'date' in request.form):
        status_msg = ""
        return render_template('quiz_add.html',status_msg=status_msg)
    elif 'subject' in request.form and 'question' in request.form and 'date' in request.form:
        n_sub = request.form['subject']
        n_question = request.form['question']
        n_date = request.form['date']
    else:
        status_msg = "Please fill the form completly"
        return render_template('quiz_add.html',status_msg=status_msg)
    con = sqlite3.connect("hw13.db")
    query = '''INSERT INTO Quiz (subject, questions, quiz_date)
                    VALUES ("%s", "%s", "%s");''' % (n_sub, n_question, n_date)
    con.execute(query)
    con.commit()
    con.close()
    return redirect('/dashboard')

# Adding Result
@app.route('/result_add', methods=['GET', 'POST'])
def result_add():
    if 'logged_in' not in session:
        return redirect('/login')

    global status_msg
    n_score = ""
    n_quizid = ""
    n_studentsid = ""
    if not ('score' in request.form and 'quizid' in request.form and 'studentsid' in request.form):
        status_msg = ""
        return render_template('result_add.html',status_msg=status_msg)
    elif 'score' in request.form and 'quizid' in request.form and 'studentsid' in request.form:
        n_score = request.form['score']
        n_quizid = request.form['quizid']
        n_studentsid = request.form['studentsid']
    else:
        status_msg = "Please fill the form completly"
        return render_template('result_add.html',status_msg=status_msg)
    con = sqlite3.connect("hw13.db")
    query = '''INSERT INTO Results (score, quiz_id, students_id)
                    VALUES ("%s", "%s", "%s");''' % (n_score, n_quizid, n_studentsid)
    con.execute(query)
    con.commit()
    con.close()
    return redirect('/dashboard')

# Details
@app.route('/report/<id>', methods=['GET', 'POST'])
def report(id):
    if 'logged_in' not in session:
        return redirect('/login')
    student_query = '''select fname, lname from Students where id == %s;'''% id

    joined_query = '''select 
                    Results.quiz_id,Quiz.quiz_date, Quiz.subject,Results.score 
                    from Results 
                    left join Quiz 
                    on Results.quiz_id = Quiz.id
                    where students_id == %s
                    order by Results.quiz_id asc;''' % id

    con = sqlite3.connect("hw13.db")
    student_data = con.execute(student_query).fetchone()
    student_name = "%s %s" % (student_data[0], student_data[1])
    quiz_report = con.execute(joined_query)
    grades = [dict(
        Quiz_ID= row[0], Quiz_Date=row[1], Quiz_Subject=row[2], Quiz_Score = row[3]) for row in quiz_report.fetchall()]
    con.commit()
    con.close()

    has_report = True
    if len(grades) == 0:
        has_report = False

    return render_template('report.html', id=id,
                           student_name=student_name,
                           grades=grades,
                           has_report=has_report)
    return redirect('/dashboard')

@app.route('/report_only', methods=['GET', 'POST'])
def report_only():
    joined_query = '''Select Students.id, Quiz.subject, Results.score, Quiz.quiz_date from Results 
                        left join Quiz 
                        on Results.quiz_id = Quiz.id
                        left join Students on
                        Results.students_id = Students.id
                        order by Students.id asc;'''
    con = sqlite3.connect("hw13.db")
    report_data = con.execute(joined_query)
    report = [dict(
        Student_ID=row[0], Quiz_Subject=row[1], Quiz_Score=row[2], Quiz_Date=row[3]) for row in report_data.fetchall()]
    con.commit()
    con.close()
    has_report = True
    if len(report) == 0:
        has_report = False
    return render_template('report_only.html',report=report,has_report=has_report)

#Delete Quiz
@app.route('/delete_quiz', methods=['GET', 'POST'])
def delete_quiz():
    if 'logged_in' not in session:
        return redirect('/login')

    delete_query = ''' Delete from Quiz where
                    id=%s;'''%request.form['quiz_id']

    delete_result_query = '''DELETE FROM Results WHERE quiz_id=%s;'''\
                          % request.form['quiz_id']

    con = sqlite3.connect("hw13.db")
    con.execute(delete_query)
    con.execute(delete_result_query)
    con.commit()
    con.close()
    return redirect("/dashboard")

#Delete Student
@app.route('/delete_student', methods=['GET', 'POST'])
def delete_student():
    if 'logged_in' not in session:
        return redirect('/login')

    delete_query = ''' Delete from Students where
                    id=%s;'''%request.form['student_id']

    delete_result_query = '''DELETE FROM Results WHERE students_id=%s;'''% request.form['student_id']

    con = sqlite3.connect("hw13.db")
    con.execute(delete_query)
    con.execute(delete_result_query)
    con.commit()
    con.close()
    return redirect("/dashboard")

@app.route('/logout')
def logout():
    session['logged_in']= False
    return redirect(url_for('login'))








if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5001'))
    except ValueError:
        PORT = 5001
    app.run(HOST, PORT)
