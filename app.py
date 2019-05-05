from flask import Flask, render_template, request, redirect, url_for, session

import sqlite3 as sql
import pandas as pd


#------ Constants Declarations ------

admin_email = 'admin@lionstate.edu'
admin_password = 'as'
semester = 'Spring 2020'


app = Flask(__name__)
app.secret_key = 'some secret key'
host = 'http://127.0.0.1:5000/'




#------------------

#------ Home ------

#------------------

@app.route("/", methods=['POST', 'GET'])
def index():
    error = None
    session['current_user'] = ""
    if request.method == 'POST':
        if request.form['email'] == admin_email and request.form['password']== admin_password:
            session['current_user'] = request.form['email']
            return redirect(url_for('admin_home'))
        student_result = valid_student(request.form['email'],request.form['password'])
        professor_result = valid_professor(request.form['email'], request.form['password'])
        if student_result:
            session['current_user'] = request.form['email']
            si = is_studentpasswordreset(request.form['email'])
            if si:
                print('reset')
                return redirect(url_for('student_home'))
            else:
                return redirect('http://127.0.0.1:5000/student/home#4')
        elif professor_result:
            session['current_user'] = request.form['email']
            pi = is_professorpasswordreset(request.form['email'])
            if pi:
                return redirect(url_for('professor_home'))
            else:
                return redirect(url_for('professor_resetpassword'))
        else:
            error = 'invalid input name'
    return render_template('index.html', error=error)




#-------------------------------

#------ Student Functions ------

#-------------------------------

@app.route('/student/home', methods=['POST', 'GET'])
def student_home():
    error = None
    username = get_studentname(session.get('current_user', None))
    if request.method == 'POST':
        p = request.form['pass']
        cp = request.form['confirmpass']
        if p == cp:
            update_studentpassword(session.get('current_user', None),request.form['pass'])
            return redirect('http://127.0.0.1:5000/student/home#1')
        else:
            error = 'invalid input name'
    result = get_studentcourses(session.get('current_user',None))
    return render_template('student.html', error=error, result = result, username = username)

@app.route("/student/<string:course>", methods=['POST', 'GET'])
def student_course(course):
    error = None
    username = get_studentname(session.get('current_user', None))
    course_result = get_courseinfo(course)
    enrolls_result = get_studentcourses(session.get('current_user',None), course)
    section = enrolls_result[0][2]
    hw_result = get_hwdetails(course, section)
    exam_result = get_examdetails(course,section)
    professor_result = get_professorinfo(course, section)
    hwgrades_result = get_hwgrades(session.get('current_user', None), course, section)
    examgrades_result = get_examgrades(session.get('current_user', None), course, section)
    course_name = course_result[0][1]
    course_desc = course_result[0][2]
    return render_template("student_course.html", error=error,
                                                    course_id = course,
                                                    section = section,
                                                    course_name = course_name,
                                                    course_desc = course_desc,
                                                    hw_result = hw_result,
                                                    exam_result = exam_result,
                                                    hwgrades_result = hwgrades_result,
                                                    examgrades_result= examgrades_result,
                                                    professor_result = professor_result,
                                                    username = username)

@app.route("/student/Cap/<string:course>", methods=['POST', 'GET'])
def student_capstone(course):
    error = None
    username = get_studentname(session.get('current_user', None))
    course_result = get_courseinfo(course)
    enrolls_result = get_studentcourses(session.get('current_user',None), course)
    section = enrolls_result[0][2]
    hw_result = get_hwdetails(course, section)
    proj_result = get_examdetails(course,section)
    professor_result = get_professorinfo(course, section)
    hwgrades_result = get_hwgrades(session.get('current_user', None), course, section)
    examgrades_result = get_examgrades(session.get('current_user', None), course, section)
    course_name = course_result[0][1]
    course_desc = course_result[0][2]
    return render_template("student_course.html", error=error,
                                                    course_id = course,
                                                    section = section,
                                                    course_name = course_name,
                                                    course_desc = course_desc,
                                                    hw_result = hw_result,
                                                    proj_result = proj_result,
                                                    hwgrades_result = hwgrades_result,
                                                    examgrades_result= examgrades_result,
                                                    professor_result = professor_result,
                                                    username = username)


@app.route('/student/editprofile', methods=['POST', 'GET'])
def student_editprofile():
    error = None
    username = get_studentname(session.get('current_user', None))
    profile_result = get_studentprofile(session.get('current_user', None))
    if profile_result[0][2] == 'M':
        male = True
        female = False
    else:
        male  = False
        female = True
    return render_template('student_editpersonal.html', error=error, username = username,male = male, female = female,
                                                                        profile_result = profile_result)



#---------------------------------

#------ Professor Functions ------

#---------------------------------

@app.route('/professor/reset_password', methods=['POST', 'GET'])
def professor_resetpassword():
    error = None

    if request.method == 'POST':
        p = request.form['pass']
        cp = request.form['confirmpass']
        if p == cp:
            update_professorpassword(session.get('current_user', None), request.form['pass'])
            return redirect(url_for('index'))
        else:
            error = 'invalid input name'
    return render_template("professor_resetpassword.html", error=error)

@app.route('/professor/home', methods = ['POST', 'GET'])
def professor_home():
    error = None
    username = get_professorname(session.get('current_user', None))
    if request.method == 'POST':
        p = request.form['pass']
        cp = request.form['confirmpass']
        if p == cp:
            update_professorpassword(session.get('current_user', None), request.form['pass'])
            return redirect(url_for('index'))
        else:
            error = 'invalid input name'
    result = get_professorcourses(session.get('current_user', None))
    return render_template('professor.html', error=error, result = result, username = username)

@app.route("/professor/Reg/<string:course>/<string:section>", methods=['POST', 'GET'])
def professor_course(course, section):
    error = None
    hw_no =1
    exam_no = 1;
    student_list = get_coursestudents(course, section)
    if request.method == 'POST':
        if "HWAdd" in request.form:
            hw_no = request.form['enter_hwno']
            hw_details = request.form['enter_hwdesc']
            add_hwdetails(course,section, hw_no, hw_details, student_list)
        if "HWDelete" in request.form:
            hw_no = request.form['hwno']
            delete_hw(course,section, hw_no)
        if "ExamAdd" in request.form:
            exam_no = request.form['enter_examno']
            exam_details = request.form['enter_examdesc']
            add_examdetails(course,section, exam_no, exam_details, student_list)
        if "ExamDelete" in request.form:
            exam_no = request.form['examno']
            delete_exam(course,section, exam_no)
        if "selectedhw" in request.form:
            hw_no = request.form['selectedhw']
            print(hw_no)
        if "selectedexam" in request.form:
            exam_no = request.form['selectedexam']
        if "HWGradeChange" in request.form:
            print(request.form)
            hw_no = request.form['HWNoGrade']
            print(hw_no)
            email = request.form['useremail']
            print(email)
            hw_newgrade = request.form['hwnewgrade']
            update_hwgrade(email,course, section, hw_no, hw_newgrade)
            print(hw_newgrade)
        if "submitFinalGrade" in request.form:
            email = request.form['selectedstudent1']
            print(email, semester, course, section)
            assign_finalgrade(email, semester, course, section)
        if "gradechange" in request.form:
            if request.form['selectedassg'] == 'Homework':
                email = request.form["selectedstudent1"]
                print(email,course,section, request.form['hweno'],request.form['hwegrade'])
                update_hwgrade(email,course,section, request.form['hweno'],request.form['hwegrade'])
            if request.form['selectedassg'] == 'Exam':
                email = request.form["selectedstudent1"]
                print(email,course,section, request.form['hweno'],request.form['hwegrade'])
                update_examgrade(email,course,section, request.form['hweno'],request.form['hwegrade'])
    stud_result = get_coursestudents(course,section)
    username = get_professorname(session.get('current_user', None))
    course_result = get_courseinfo(course)
    hw_result = get_hwdetails(course, section)
    exam_result = get_examdetails(course,section)
    students_hwgrade_result = get_students_hwgrades(course,section,hw_no)
    students_examgrade_result = get_students_examgrades(course, section, exam_no)
    course_name = course_result[0][1]
    course_desc = course_result[0][2]
    return render_template("professor_course.html", error=error,
                                                    username = username,
                                                    course_id = course,
                                                    shw_no = hw_no,
                                                    sexam_no=exam_no,
                                                    students_hwgrade_result = students_hwgrade_result,
                                                    students_examgrade_result=students_examgrade_result,
                                                    stud_result = stud_result,
                                                    student_list = student_list,
                                                    hw_result = hw_result,
                                                    exam_result =  exam_result,
                                                    section = section,
                                                    course_name = course_name,
                                                    course_desc = course_desc)

@app.route("/professor/Cap/<string:course>/<string:section>", methods=['POST', 'GET'])
def professor_capstone(course, section):
    error = None
    hw_no =1
    proj_no = 1;
    prof_list = get_allprof()
    student_list = get_coursestudents(course, section)

    if request.method == 'POST':
        if "HWAdd" in request.form:
            hw_no = request.form['enter_hwno']
            hw_details = request.form['enter_hwdesc']
            add_hwdetails(course,section, hw_no, hw_details, student_list)
        if "HWDelete" in request.form:
            hw_no = request.form['hwno']
            delete_hw(course,section, hw_no)
        if "TeamAdd" in request.form:
            proj_no = request.form['enter_projno1']
            teamid = request.form['enter_teamno']
            add_teamdetails(course,section, teamid, proj_no)
        if "TeamDelete" in request.form:
            teamid = request.form['teamno']
            delete_team(course,section, teamid)
        if "ProjAdd" in request.form:
            proj_no = request.form['enter_projno']
            sponser = request.form['selectedsponsor1']
            add_projdetails(course,section, proj_no, sponser, [1,2])
        if "ProjDelete" in request.form:
            proj_no = request.form['projno']
            delete_proj(course,section, proj_no)
        if "selectedhw" in request.form:
            hw_no = request.form['selectedhw']
            print(hw_no)

        if "selectedexam" in request.form:
            exam_no = request.form['selectedexam']
        if "HWGradeChange" in request.form:
            print(request.form)
            hw_no = request.form['HWNoGrade']
            print(hw_no)
            email = request.form['useremail']
            print(email)
            hw_newgrade = request.form['hwnewgrade']
            update_hwgrade(email,course, section, hw_no, hw_newgrade)
            print(hw_newgrade)
        if "submitFinalGrade" in request.form:
            email = request.form['selectedstudent1']
            print(email, semester, course, section)
            assign_finalgrade(email, semester, course, section)

    team_result = get_teamdetails(course,section)
    username = get_professorname(session.get('current_user', None))
    course_result = get_courseinfo(course)
    hw_result = get_hwdetails(course, section)
    proj_result = get_projdetails(course,section)
    students_hwgrade_result = get_students_hwgrades(course,section,hw_no)
    course_name = course_result[0][1]
    course_desc = course_result[0][2]
    return render_template("professor_capstone.html", error=error,
                                                    username = username,
                                                    course_id = course,
                                                    shw_no = hw_no,
                                                    team_result = team_result,
                                                    students_hwgrade_result = students_hwgrade_result,
                                                    student_list = student_list,
                                                    hw_result = hw_result,
                                                    prof_list = prof_list,
                                                    proj_result =  proj_result,
                                                    section = section,
                                                    course_name = course_name,
                                                    course_desc = course_desc)



#-------------------------------

#------ Admin Functions ------

#-------------------------------

@app.route('/admin/dashboard', methods=['POST', 'GET'])
def admin_home():
    error = None
    course_result = get_allcourses()
    prof_result = get_allprof()
    stud_result = get_allstud()
    if request.method == 'POST':
        if "CourseAdd" in request.form:
            courseno = request.form['enter_courseid']
            coursename = request.form['enter_courseno']
            coursedetails = request.form['enter_coursedesc']
            add_course(courseno, coursename, coursedetails)
        if "CourseDelete" in request.form:
            course_id = request.form['courseid']
            print(course_id)
            delete_course(course_id)
        if "AssignProf" in request.form:
            selectedttid = request.form['selectedprofessor']
            selectedcourse = request.form['selectedcourse']
            selectedsectiontype = request.form['selectedsectiontype']
            selectedsection = request.form['selectedsection']
            selectedsectionlimit = request.form['seclimit']
            add_section(selectedcourse,selectedsection,selectedsectiontype,selectedsectionlimit, selectedttid)
        if "AssignStudent" in request.form:
            selectedstud = request.form['selectedstudent1']
            selectedcourse = request.form['selectedcourse1']
            selectedsection = request.form['selectedsection1']
            add_enroll(selectedstud, selectedcourse, selectedsection)
    stud_result = get_allstud()
    prof_result = get_allprof()
    course_result = get_allcourses()

    return render_template('admin.html', error=error, prof_result = prof_result, stud_result = stud_result, course_result = course_result)



#---------------------------

#------ SQL Functions ------

#---------------------------



#------ SELECT Functions ------


def get_allcourses():
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM Course order by course_id')
    r = cursor.fetchall()
    return r

def get_allprof():
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT p.email, p.name, pt.teaching_team_id FROM Professor p, Prof_team_members pt WHERE pt.prof_email = p.email order by p.name')
    r = cursor.fetchall()
    return r

def get_allstud():
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT email, name FROM Student')
    r = cursor.fetchall()
    return r

def is_studentpasswordreset(email):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT password_reset FROM Student WHERE email = ?;',(email,))
    r = cursor.fetchall()
    return r[0][0]

def is_professorpasswordreset(email):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT password_reset FROM Professor WHERE email = ?;',(email,))
    r = cursor.fetchall()
    return r[0][0]

def is_capstone(email):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT password_reset FROM Student WHERE email = ?;',(email,))
    r = cursor.fetchall()
    return r

def valid_student(email, password):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM Student WHERE email = ? and password= ?;',(email, password))
    return cursor.fetchone()

def valid_professor(email, password):
    connection = sql.connect('database.db')
    connection.execute('CREATE TABLE IF NOT EXISTS Professor(email TEXT, password TEXT, name TEXT, age INTEGER, gender TEXT, office_address TEXT, department TEXT, title, TEXT);')
    cursor = connection.execute('SELECT * FROM Professor WHERE email = ? and password= ?;',(email, password))
    return cursor.fetchone()

def get_professorinfo(course, section):
    connection = sql.connect('database.db')
    cursor = connection.execute("SELECT p.name, p.email, p.office_address "
                                "FROM Section s, Prof_team_members pt, Professor p "
                                "WHERE   s.course_id = ? AND "
                                        "s.sec_no = ? AND pt.teaching_team_id = s.teaching_team_id AND "
                                        "pt.prof_email = p.email;",(course,section))
    r = cursor.fetchall()
    return r

def get_studentprofile(email):
    connection = sql.connect('database.db')
    cursor = connection.execute("SELECT s.email, s.name, s.age, s.gender, s.street, s.zipcode, z.city, z.state "
                                "FROM Student s, Zipcode z "
                                "WHERE   s.zipcode = z.zipcode AND "
                                        "s.email = ? ",(email,))
    r = cursor.fetchall()
    return r

def get_hwdetails(course_id, sec_no):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM Homework WHERE course_id = ? and sec_no = ?;', (course_id,sec_no))
    r = cursor.fetchall()
    return r

def get_hwgrades(student, course, section):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT h.hw_no, h.grade, max(h1.grade), min(h1.grade), avg(h1.grade) FROM Homework_grades h, Homework_grades h1 where h.student_email = ? AND h.course_id = ? AND h.sec_no = ? and h.course_id = h1.course_id and h.sec_no = h1.sec_no and h.hw_no = h1.hw_no;', (student, course, section))
    r = cursor.fetchall()
    return r

def get_max_min_avggrades(student, course, section):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT hw_no, max(grade), min(grade), avg(grade) FROM Homework_grades WHERE AND course_id = ? AND sec_no = ?;', (student, course, section))
    r = cursor.fetchall()
    return r

def get_courseinfo(course_id):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM Course WHERE course_id = ?;',(course_id,))
    r = cursor.fetchall()
    return r

def get_examdetails(course, section):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM Exam WHERE course_id = ? and sec_no = ?;', (course, section))
    r = cursor.fetchall()
    return r

def get_teamdetails(course, section):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM Capstone_Team WHERE course_id = ? and sec_no = ?;', (course, section))
    r = cursor.fetchall()
    return r

def get_projdetails(course, section):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM Capstone_section WHERE course_id = ? and sec_no = ? order by project_no;', (course, section))
    r = cursor.fetchall()
    return r

def get_examgrades(student, course, section):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT e.exam_no, e.grade, max(e1.grade),min(e1.grade),avg(e1.grade) FROM Exam_grades e, Exam_grades e1 WHERE e.student_email = ? AND e.course_id = ? AND e.sec_no = ? and e.course_id = e1.course_id and e.sec_no = e1.sec_no and e.exam_no = e1.exam_no;', (student, course, section))
    r = cursor.fetchall()
    return r

def get_studentcourses(email,courseid = ""):
    connection = sql.connect('database.db')
    statement = 'SELECT * FROM Enrolls WHERE student_email = ?'
    if courseid != "":
        statement = statement + 'and course_id = ?;'
        cursor = connection.execute(statement, (email, courseid))
        return cursor.fetchall()
    statement = statement + ';'
    cursor = connection.execute(statement,(email,))
    return cursor.fetchall()

def get_professorcourses(email):
    connection = sql.connect('database.db')
    cursor = connection.execute("SELECT s.course_id, s.sec_no, s.course_id||'/'||s.sec_no as path, s.section_type||'/' as type FROM Section s, Prof_team_members Pt WHERE Pt.prof_email = ? AND Pt.teaching_team_id = s.teaching_team_id;", (email,))
    r = cursor.fetchall()
    return r

def get_studentname(email):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM Student WHERE email = ?;',(email, ))
    r = cursor.fetchall()
    return r[0][2]

def get_professorname(email):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM Professor WHERE email = ?;',(email, ))
    r = cursor.fetchall()
    return r[0][2]

def get_coursestudents(course,section):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT s.name, s.email FROM Enrolls e, Student s WHERE e.student_email = s.email AND e.course_id = ? AND e.section_no = ?;', (course,section))
    r = cursor.fetchall()
    return r

def get_students_hwgrades(course, section, hw_no):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT hg.hw_no, s.name, s.email, hg.grade FROM Homework_grades hg, Student s WHERE hg.student_email = s.email AND hg.course_id = ? AND hg.sec_no = ? AND hg.hw_no = ?;', (course, section, hw_no))
    r = cursor.fetchall()
    return r

def get_students_examgrades(course, section, exam_no):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT eg.exam_no, s.name, s.email, eg.grade FROM Exam_grades eg, Student s WHERE eg.student_email = s.email AND eg.course_id = ? AND eg.sec_no = ? AND eg.exam_no = ?;', (course, section, exam_no))
    r = cursor.fetchall()
    return r



#------ UPDATE Functions ------

def update_studentpassword(email, password):
    connection = sql.connect('database.db')
    connection.execute('UPDATE Student SET password = ?, password_reset = true WHERE email = ?;', (password, email))
    connection.commit()

def update_professorpassword(email, password):
    connection = sql.connect('database.db')
    connection.execute('UPDATE Professor SET password = ?, password_reset = true WHERE email = ?;', (password, email))
    connection.commit()

def update_hwgrade(email, course, section, hwno, grade):
    connection = sql.connect('database.db')
    connection.execute('UPDATE Homework_grades SET grade = ? WHERE student_email = ? AND course_id = ? AND sec_no =? AND hw_no =?;', (grade,email,course,section,hwno))
    connection.commit()

def update_examgrade(email, course, section, examno, grade):
    connection = sql.connect('database.db')
    print(email, course, section, examno, grade)
    connection.execute('UPDATE Exam_grades SET grade = ? WHERE student_email = ? AND course_id = ? AND sec_no =? AND exam_no =?;', (grade,email,course,section,examno))
    connection.commit()

def update_teamgrade(email, course, section, teamid, grade):
    connection = sql.connect('database.db')
    cursor = connection.execute('select student_email from Capstone_Team_Members where capstone_team_id=?',(teamid))
    r =cursor.fetchall()
    for i in r:
        connection.execute(
            'UPDATE Capstone_grades SET grade = ? WHERE capstone_team_id = ? AND course_id = ? AND sec_no =?;',
            (grade, email, course, section))
        connection.commit()


#------ INSERT FUNCTIONS ------

def add_hwdetails(course_id, sec_no, hw_no, hw_details, studentlist):
    connection = sql.connect('database.db')
    connection.execute('INSERT OR REPLACE INTO Homework (course_id,sec_no, hw_no, hw_details) VALUES (?,?,?,?);', (course_id, sec_no, hw_no, hw_details))
    for i,j in studentlist:
        connection.execute('INSERT OR REPLACE INTO Homework_grades (student_email, course_id,sec_no, hw_no) VALUES (?,?,?,?);',(j,course_id, sec_no, hw_no))
    connection.commit()

def add_examdetails(course_id, sec_no, exam_no, exam_details, studentlist):
    connection = sql.connect('database.db')
    connection.execute('INSERT OR REPLACE INTO Exam (course_id,sec_no, exam_no, exam_details) VALUES (?,?,?,?);', (course_id, sec_no, exam_no, exam_details))
    for i, j in studentlist:
        connection.execute('INSERT OR REPLACE INTO Exam_grades (student_email, course_id,sec_no, exam_no) VALUES (?,?,?,?);',(j, course_id, sec_no, exam_no))
    connection.commit()

def add_projdetails(course_id, sec_no, proj_no, sponsor, capstoneteam):
    connection = sql.connect('database.db')
    print(course_id,sec_no,proj_no,sponsor)
    connection.execute('INSERT OR REPLACE INTO Capstone_section (course_id,sec_no, project_no, sponsor_id) VALUES (?,?,?,?);', (course_id, sec_no, proj_no, sponsor))
    for i in capstoneteam:
        connection.execute(
            'INSERT OR REPLACE INTO Capstone_grades (course_id,sec_no, capstone_team_id) VALUES (?,?,?);',
            (course_id, sec_no, i))
    connection.commit()

def add_teamdetails(course_id, sec_no, teamid, proj_no):
    connection = sql.connect('database.db')
    connection.execute('INSERT OR REPLACE INTO Capstone_Team (course_id,sec_no, capstone_team_id, project_no) VALUES (?,?,?,?);', (course_id, sec_no, teamid, proj_no))
    connection.commit()

def add_course(course_id, course_name, course_desc):
    connection = sql.connect('database.db')
    connection.execute('INSERT OR REPLACE INTO Course (course_id,course_name, course_description) VALUES (?,?,?);',
                       (course_id, course_name, course_desc))
    connection.commit()

def add_section(course,sec,type,limit,ttid):
    connection = sql.connect('database.db')
    connection.execute('INSERT OR REPLACE INTO Section (course_id,sec_no,section_type, section_limit, teaching_team_id) VALUES (?,?,?,?,?);',
                       (course,sec,type,limit, ttid))
    connection.commit()

def add_enroll(email,course,sec):
    connection = sql.connect('database.db')
    r1 = connection.execute('select count(student_email) from Enrolls where course_id = ? and section_no = ?;',(course,sec))
    r2 = connection.execute('select section_limit from Section where course_id=? and sec_no = ?',(course,sec))
    count = r1.fetchone()
    section = r2.fetchone()
    #checks if number of students <capacity
    if count[0] < section[0]:
        connection.execute('INSERT OR REPLACE INTO Enrolls (student_email,course_id,section_no) VALUES (?,?,?);',
                       (email,course,sec))
        connection.commit()

def assign_finalgrade(email, semester, course, section):
    connection = sql.connect('database.db')
    cursor1 = connection.execute('select avg(grade) from Exam_grades where student_email =? and course_id =? and sec_no =?',(email, course, section))
    avg_examgrade = cursor1.fetchone()
    print(avg_examgrade)
    cursor2 = connection.execute('select avg(grade) from Homework_grades where student_email =? and course_id =? and sec_no =?',(email, course, section))
    avg_hwgrade = cursor2.fetchone()
    print(avg_hwgrade)

    finalgrade = (float(avg_examgrade[0])+float(avg_hwgrade[0]))/2
    print(avg_hwgrade,avg_examgrade,finalgrade)
    if finalgrade> 90:
        fg = 'A'
    elif finalgrade>80:
        fg = 'B'
    elif finalgrade>70:
        fg = 'C'
    elif finalgrade>60:
        fg = 'D'
    else:
        fg = 'F'
    connection.execute('insert or replace into Final_grade (email,semester, grade, course_id) values (?,?,?,?)',(email, semester, fg, course))
    connection.commit()


#------DELETE FUNCTIONS ------

def delete_hw(course_id, sec_no, hw_no):
    connection = sql.connect('database.db')
    connection.execute('DELETE FROM Homework WHERE course_id = ? AND sec_no = ? AND hw_no = ?;', (course_id, sec_no, hw_no))
    connection.commit()
    connection.execute('DELETE FROM Homework_grades WHERE course_id = ? AND sec_no = ? AND hw_no = ?;',(course_id, sec_no, hw_no))
    connection.commit()

def delete_course(course_id):
    connection = sql.connect('database.db')
    connection.execute('DELETE FROM Course WHERE course_id = ?;', (course_id,))
    connection.commit()
    connection.execute('DELETE FROM Enrolls WHERE course_id = ?;', (course_id,))
    connection.commit()
    connection.execute('DELETE FROM Section WHERE course_id = ?;', (course_id,))
    connection.commit()

def delete_exam(course_id, sec_no, exam_no):
    connection = sql.connect('database.db')
    print(course_id, sec_no)
    connection.execute('DELETE FROM Exam WHERE course_id = ? AND sec_no = ? AND exam_no = ?;', (course_id, sec_no, exam_no))
    connection.commit()
    connection.execute('DELETE FROM Exam_grades WHERE course_id = ? AND sec_no = ? AND exam_no = ?;',(course_id, sec_no, exam_no))
    connection.commit()

def delete_proj(course_id, sec_no, proj_no):
    connection = sql.connect('database.db')
    print(course_id, sec_no)
    connection.execute('DELETE FROM Capstone_section WHERE course_id = ? AND sec_no = ? AND project_no = ?;', (course_id, sec_no, proj_no))
    connection.commit()
    connection.execute('DELETE FROM Capstone_Team WHERE course_id = ? AND sec_no = ? AND project_no = ?;',(course_id, sec_no, proj_no))
    connection.commit()

def delete_team(course_id, sec_no, teamid):
    connection = sql.connect('database.db')
    print(course_id, sec_no)
    connection.execute('DELETE FROM Capstone_Team WHERE course_id = ? AND sec_no = ? AND capstone_team_id = ?;', (course_id, sec_no, teamid))
    connection.commit()



