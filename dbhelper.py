#dbhelper.py
from sqlite3 import connect, Row
import sqlite3

DATABASE = 'students.db'

def get_db_connection():
    """Establishes a new database connection."""
    db = connect(DATABASE)
    db.row_factory = Row  # Set the row factory to Row for dictionary-like access
    return db


def userlogin(username: str, password: str) -> bool:
    sql = "SELECT * FROM users WHERE username = ? AND password = ?"
    db = connect(DATABASE)
    cursor = db.cursor()
    cursor.row_factory = Row
    cursor.execute(sql, (username, password))
    data = cursor.fetchall()
    cursor.close()
    db.close()
    return len(data) > 0

def getall_students():
    sql = "SELECT * FROM students"
    db = connect(DATABASE)
    cursor = db.cursor()
    cursor.row_factory = Row
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    db.close()
    return data

def add_student(idno, lastname, firstname, course, level, image):
    try:
        connection = sqlite3.connect('students.db')
        cursor = connection.cursor()

        sql = '''INSERT INTO students (idno, lastname, firstname, course, level, image)
                 VALUES (?, ?, ?, ?, ?, ?)'''
        cursor.execute(sql, (idno, lastname, firstname, course, level, image))
        connection.commit()
        return True  # Indicate success
    except sqlite3.IntegrityError:
        return False  # Indicate failure due to unique constraint
    finally:
        connection.close()

def get_student_image_path(idno):
    sql = "SELECT image FROM students WHERE idno = ?"
    db = connect(DATABASE)
    cursor = db.cursor()
    cursor.row_factory = Row
    cursor.execute(sql, (idno,))
    data = cursor.fetchone()
    cursor.close()
    db.close()
    return data["image"] if data else None

# New function to delete a student record
def delete_student_record(idno):
    sql = "DELETE FROM students WHERE idno = ?"
    db = connect(DATABASE)
    cursor = db.cursor()
    cursor.execute(sql, (idno,))
    db.commit()
    cursor.close()
    db.close()
    
def student_exists(idno):
    sql = "SELECT * FROM students WHERE idno = ?"
    db = connect('students.db')
    cursor = db.cursor()
    cursor.execute(sql, (idno,))
    exists = cursor.fetchone() is not None
    cursor.close()
    db.close()
    return exists
