#app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from dbhelper import *
from flask_session import Session
import os
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config["SESSION_TYPE"] = "filesystem"
app.config['SESSION_PERMANENT'] = False
Session(app)


def userlogin(username: str, password: str) -> bool:
    sql = "SELECT * FROM users WHERE username = ? AND password = ?"
    db = connect('students.db')
    cursor = db.cursor()
    cursor.row_factory = Row
    cursor.execute(sql, (username, password))
    data = cursor.fetchall()
    cursor.close()
    db.close()
    return len(data) > 0

def getall_students():
    sql = "SELECT * FROM students"
    db = connect('students.db')
    cursor = db.cursor()
    cursor.row_factory = Row
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    db.close()
    return data

@app.route('/login', methods=['POST', 'GET'])
def login():
    pagetitle = "User Login"
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return jsonify(error="Both username and password are required"), 400
        
        if userlogin(username, password):
            session['username'] = username
            return jsonify(redirect=url_for('student_list'))
        else:
            return jsonify(error="Invalid username or password"), 400

    return render_template('login.html', pagetitle=pagetitle)

@app.route('/students')
def student_list():
    if 'username' in session:
        pagetitle = "Student List"
        return render_template('index.html', data=getall_students(), pagetitle=pagetitle)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')  # Optional: Add a flash message
    return redirect(url_for('login'))

@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/add_student', methods=['GET', 'POST'])
def add_student_route():
    if request.method == 'POST':
        idno = request.form.get('idno')
        lastname = request.form.get('lastname')
        firstname = request.form.get('firstname')
        course = request.form.get('course')
        level = request.form.get('level')
        image_data = request.form.get('image_data')  # Base64 image data

        # Logging for debugging
        app.logger.debug("Received form data: %s", request.form)

        if not idno or not lastname or not firstname or not course or not level or not image_data:
            return jsonify({'status': 'error', 'message': 'All fields are required!'}), 400

        if student_exists(idno):  # Ensure this function is implemented
            return jsonify({'status': 'error', 'message': 'Student with this ID already exists!'}), 400

        try:
            # Decode and save image
            img_data = base64.b64decode(image_data.split(",")[1])
            image_path = f'static/images/{idno}_profile.jpg'
            with open(image_path, 'wb') as f:
                f.write(img_data)

            add_student(idno, lastname, firstname, course, level, image_path)
            return jsonify({'status': 'success'})
        except Exception as e:
            app.logger.error("Error adding student: %s", e)
            return jsonify({'status': 'error', 'message': 'An error occurred while adding the student.'}), 500

    return render_template('addstudents.html', pagetitle="Add Student")


@app.route('/update_student', methods=['POST'])
def update_student():
    idno = request.form['idno']
    lastname = request.form['lastname']
    firstname = request.form['firstname']
    course = request.form['course']
    level = request.form['level']

    # Update the database record
    sql = "UPDATE students SET lastname = ?, firstname = ?, course = ?, level = ? WHERE idno = ?"
    db = connect('students.db')
    cursor = db.cursor()
    cursor.execute(sql, (lastname, firstname, course, level, idno))
    db.commit()
    cursor.close()
    db.close()

    flash('Student updated successfully!', 'success')
    return redirect(url_for('student_list'))

@app.route('/delete_student', methods=['POST'])
def delete_student():
    idno = request.form['idno']
    
    # Retrieve the student's image path
    image_path = get_student_image_path(idno)
    
    # Delete the student record from the database
    delete_student_record(idno)
    
    # Remove the image file if it exists
    if image_path and os.path.exists(image_path):
        try:
            os.remove(image_path)
        except OSError as e:
            flash(f"Error deleting image: {e}", 'error')

    flash("Student and associated image deleted successfully", 'success')
    return redirect(url_for('student_list'))

@app.after_request
def after_request(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response



if __name__ == '__main__':
    app.run(debug=True) 