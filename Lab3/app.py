
from bottle import get, post, run, request, response
import sqlite3
from urllib.parse import unquote

PORT = 7007


db = sqlite3.connect('movies.sqlite')

@get('/ping')
def get_ping():
    string = "pong"
   
    response.status = 200
    found = [{"string": string}]
    return {string}

@post('/reset')
def reset():
    c = db.cursor()
    #c.execute("PRAGMA foreign_keys=ON;")
    tables = ["theaters", "movies", "screenings", "tickets", "customers"]
    for table in tables:
        c.execute(
           f"""
           DELETE
           FROM {table}
            """)

    c.execute(
        """
        INSERT
         INTO theaters(theater_name, capacity)
          VALUES ('Kino', 10),
                ('Regal', 16),
                ('Skandia', 100)
          """
    )
    db.commit()
    response.status = 200
    return "yihaa"


@post('/users')
def post_users():
    user = request.json
    username = user['username']
    full_name = user['fullName']
    pwd = user['pwd']
    c = db.cursor()
    try: 
        c.execute(
            """
            INSERT 
            INTO  customers(user_name, full_name, password)
            VALUES (?,?,?)
            RETURNING user_name
            """,
            [username, full_name, pwd]
        )
        found = c.fetchone()
        if not found:
            response.status = 400
            return "Illegal..."
        else:
            db.commit()
            response.status = 201
            username, = found
            return f"/users/{username}"
    except sqlite3.IntegrityError:
        response.status = 400
        return "fanns redan"

@post('/movies')
def post_movies():
    movie = request.json
    imdb_key = movie['imdbKey']
    title = movie['title']
    year = movie['year']
    c = db.cursor()
    try: 
        c.execute(
            """
            INSERT 
            INTO  movies(imdb_key, movie_title, production_year)
            VALUES (?,?,?)
            RETURNING imdb_key
            """,
            [imdb_key, title, year]
        )
        found = c.fetchone()
        if not found:
            response.status = 400
            return "Illegal..."
        else:
            db.commit()
            response.status = 201
            imdbkey, = found
            return f"/movies/{imdbkey}"
    except sqlite3.IntegrityError:
        response.status = 400
        return ""

@post('/performances')
def post_performances():
    performance = request.json
    imdb_key = performance['imdbKey']
    theater = performance['theater']
    date = performance['date']
    time = performance['time']
    c = db.cursor()
    try: 
        c.execute(
            """
            SELECT capacity 
            FROM theaters
            WHERE theater_name = ?
            """,
            [theater])
        capacity, = c.fetchone()
        print(capacity)

        c.execute(
            """
            INSERT 
            INTO  screenings(start_time, start_date, theater_name, imdb_key, remaining_seats)
            VALUES (?,?,?,?,?)
            RETURNING screening_id
            """,
            [time, date, theater, imdb_key, capacity]
        )
        found = c.fetchone()
        if not found:
            response.status = 400
            return "Illegal..."
        else:
            db.commit()
            response.status = 201
            screening_id, = found
            return f"/performances/{screening_id}"
    except sqlite3.IntegrityError:
        response.status = 400
        return "No such movie or theater"

@get('/movies')
def get_movies():
    c = db.cursor()
    c.execute(
        """
        SELECT imdb_key, movie_title, production_year 
        FROM movies
        """
    )
    found = [{"imdbKey":imdb_key,
                "title": title,
                "year": year} for imdb_key, title, year in c ]
    return {"data": found}

@get('/movies/<imdbKey>')
def get_movies(imdbKey):
    c = db.cursor()
    c.execute(
        """
        SELECT imdb_key, movie_title, production_year 
        FROM movies
        WHERE imdb_key = ?
        """,
        [imdbKey]
    )
    found = [{"imdbKey":imdb_key,
                "title": title,
                "year": year} for imdb_key, title, year in c ]
    return {"data": found}

@get('/performances')
def get_performances():
    c = db.cursor()
    c.execute(
        """
        SELECT *
        FROM screenings
        JOIN movies USING (imdb_key)
        """
    )
    found = [{"performanceId": performance_id,
                "date": date,
                "startTime": start_time,
                "title": title,
                "year": year,
                "theater": theater,
                "remainingSeats": remaining_seats} for performance_id, start_time, date, theater,
                  _, remaining_seats, title, year, _  in c ]
    return {"data": found}


@post('/tickets')
def post_tickets():
    ticket = request.json
    user_name = ticket['username']
    password = ticket['pwd']
    screening_id =ticket['performanceId']
    c = db.cursor()


    ### Kolla om user och password is wrong  

    c.execute("""
              SELECT user_name, password
              FROM customers
              WHERE  user_name = ?  AND password = ?
              """
              ,[user_name, password])
    found = c.fetchone()
    if not found:
        response.status = 401
        return "Wrong user Credentials"

    c.execute(
        """
        SELECT count()
        FROM tickets
        GROUP BY screening_id
        HAVING screening_id = ?
        """,[screening_id]
    )
    found = c.fetchone()

    if not found:
        nbrtickets = 0
    else:
        nbrtickets, = found
    print(nbrtickets)
    
    c.execute(
        """
    SELECT capacity
    FROM theaters
    WHERE theater_name IN (
        SELECT theater_name 
        FROM screenings
        WHERE screening_id = ?
    ) 
    """, [screening_id]
    )
    found = c.fetchone()
    capacity, = found
    print(capacity)
    if capacity - nbrtickets > 0:
        c.execute("""
                INSERT
                  INTO tickets(user_name, screening_id)
                  VALUES (?, ?)
                  RETURNING ticket_id
                  """,[user_name, screening_id])
        found = c.fetchone()
        ticket_id, = found


        c.execute("""
                UPDATE screenings
                SET remaining_seats = remaining_seats -1
                RETURNING remaining_seats
                  """)
        found = c.fetchone()
        remaining_seats, = found
        print(f"remaining seats = {remaining_seats}")
        response.status = 201
        return f"/tickets/{ticket_id}"
     
    elif capacity - nbrtickets == 0:
        response.status = 400
        return "No tickets left"

    else:
        response.status = 400
        return "error" 


@get('/users/<username>/tickets')
def get_tickets(username):
    c = db.cursor()
    c.execute("""
              WITH nbrtickets AS (SELECT *
              FROM customers
              JOIN tickets USING (user_name)
              WHERE user_name = ?)
              ,

            movie_info AS (SELECT * 
              FROM screenings
              JOIN movies USING (imdb_key))

            SELECT start_date, start_time, theater_name, movie_title, production_year, count() as numberOftickets
            FROM movie_info 
            JOIN nbrtickets USING (screening_id)
            GROUP BY screening_id
              """,[username])
    
    found = [{"date": date, "startTime": starttime, "theater": theater_name, "title": title,
              "year": year, "nbrOfTickets": nbroftickets}
              for date, starttime, theater_name, title, year, nbroftickets in c ]
    return {"data": found}






run(host='127.0.0.1', port=PORT)
