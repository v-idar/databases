
from bottle import get, post, run, request, response
import sqlite3
from urllib.parse import unquote

PORT = 4567


db = sqlite3.connect('colleges.sqlite')


@get('/students')
def get_students():
    query = """
        SELECT   s_id, s_name, gpa
        FROM     students
        WHERE    TRUE
        """
    params = []

    if request.query.name:
        query += "AND s_name = ?"
        params.append(unquote(request.query.name))
    if request.query.minGpa:
        query += "AND gpa >= ?"
        params.append(request.query.minGpa)
    c = db.cursor()
    c.execute(
        query,
        params
    )
    response.status = 200
    found = [{"id": id, "name": name, "gpa": grade} for id, name, grade in c]
    return {"data": found}


def first_get_students():
    c = db.cursor()
    c.execute(
        """
        SELECT   s_id, s_name, gpa
        FROM     students
        """
    )
    response.status = 200
    found = [{"id": id, "name": name, "gpa": grade} for id, name, grade in c]
    return {"data": found}


@get('/students/<s_id>')
def get_student(s_id):
    c = db.cursor()
    c.execute(
        """
        SELECT   s_id, s_name, gpa
        FROM     students
        WHERE    s_id = ?
        """,
        [s_id]
    )
    found = [{"id": id,
              "name": name,
              "gpa": grade} for id, name, grade in c]
    if len(found) == 0:
        response.status = 404
        return "Didn't find student"
    return {"data": found}


@post('/students')
def post_student():
    student = request.json
    c = db.cursor()
    try:
        c.execute(
            """
            INSERT
            INTO   students(s_id, s_name, gpa)
            VALUES (?,?,?)
            RETURNING  s_id
            """,
            [student['id'], student['name'], student['gpa']]
        )
        found = c.fetchone()
        if not found:
            response.status = 400
            return "Illegal..."
        else:
            db.commit()
            response.status = 201
            s_id, = found
            return f"http://localhost:{PORT}/{s_id}"
    except sqlite3.IntegrityError:
        response.status = 409
        return "Student id already in use"


run(host='localhost', port=PORT)
