from flask import Flask, redirect, url_for, render_template, request, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'super secret key'

# Home Page
@app.route('/')
def home():
    logstatus = 'false'
    return render_template("home.html", logstatus = session.get('logstatus', None))

# Bikes Page
@app.route('/bikes', methods=["GET","POST"])
def bikes():
    logstatus = 'false'
    conn = sqlite3.connect('Beamma-Bikes.db')
    c = conn.cursor()
    c.execute("SELECT id, name FROM brand")
    brands = c.fetchall()
    c.execute("SELECT id, name FROM type")
    types = c.fetchall()
    c.execute("SELECT DISTINCT year FROM bikes ORDER BY year DESC")
    years = c.fetchall()
    c.execute("SELECT id, size FROM sizes ORDER BY id ASC")
    sizes = c.fetchall()
    filter_options = dict(brand=brands, type=types, year=years, sid=sizes)

	# FILTER SYSTEM
    if request.method == 'POST':

		# Variables
        query = "SELECT DISTINCT bikes.name, bikes.image, bikes.id FROM bikes INNER JOIN bikes_sizes ON bikes_sizes.bid = bikes.id "
        parms = []
        filters = []

        # Build Query
        for key in request.form:
            if key == "sort": continue # Ignore Sort
            values = request.form.getlist(key)
            column = "bikes_sizes." + key if key == "sid" else 'bikes.' + key
            filters.append(f"{column} IN (" + ", ".join(['?']*len(values)) + ") ")
            parms += values
        if filters:
            query += " WHERE " + " AND ".join(filters)
        query += request.form.getlist("sort")[0]

        print(query, parms)

		# Execute Query
        conn = sqlite3.connect('Beamma-Bikes.db')
        c = conn.cursor()
        c.execute(query, parms)
        bikes = c.fetchall()
        conn.close()
        return render_template("bikes.html", bikes = bikes, filter_options = filter_options, logstatus = session.get('logstatus', None))

	# Normal Page Loading
    else:

		# Connect to databse and preform query
        conn = sqlite3.connect('Beamma-Bikes.db')
        c = conn.cursor()
        c.execute("SELECT name, image, id FROM Bikes")
        bikes = c.fetchall()
        conn.close()
        return render_template("bikes.html", bikes = bikes, filter_options = filter_options, logstatus = session.get('logstatus', None))

@app.route("/bikes/<id>")
def bike(id):
    logstatus = 'false'
    conn = sqlite3.connect('Beamma-Bikes.db')
    c = conn.cursor()
    c.execute("SELECT bikes.name, bikes.image, bikes.price, bikes.description, brand.name FROM bikes INNER JOIN brand ON bikes.brand = brand.id WHERE bikes.id=?", (id,))
    bikes = c.fetchall()
    conn.close()

    return render_template("select_bike.html", bikes = bikes[0], logstatus = session.get('logstatus', None))

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user_name = request.form.get("user_name")
        password = request.form.get("password")
        if user_name and password:
            print(user_name)
            print(password)
            conn = sqlite3.connect('Beamma-Bikes.db')
            c = conn.cursor()
            c.execute("SELECT password FROM users WHERE name=?",(user_name,))
            log_password = c.fetchall()
            conn.close()
            log_password = log_password[0]
            print(log_password[0])
            log_status = check_password_hash(log_password[0], password)
            if log_status is True:
                session['logstatus'] = 'true'
                return redirect(url_for('bikes'))
            else:
                session['logstatus'] = 'false'
                print("Failed")

        return render_template("login.html")
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        user_name = request.form.get("user_name")
        hashed_password = generate_password_hash(request.form.get("password"), salt_length=10)
        print(hashed_password)
        conn = sqlite3.connect('Beamma-Bikes.db')
        cur = conn.cursor()
        SQL = "INSERT INTO users(name,password) VALUES(?,?)"
        cur = conn.cursor()
        cur.execute(SQL,[user_name, hashed_password])
        conn.commit()
        conn.close()

        return render_template("register.html")
    else:
        return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True)
