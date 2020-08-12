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

@app.route("/bikes/<id>", methods=["GET", "POST"])
def bike(id):
    logstatus = 'false'
    conn = sqlite3.connect('Beamma-Bikes.db')
    c = conn.cursor()
    c.execute("SELECT bikes.name, bikes.image, bikes.price, bikes.description, brand.name FROM bikes INNER JOIN brand ON bikes.brand = brand.id WHERE bikes.id=?", (id,))
    bikes = c.fetchall()
    conn.close()
    if request.method == "POST":
        user_id = session.get('logstatus', None)
        print(user_id)
        conn = sqlite3.connect('Beamma-Bikes.db')
        c = conn.cursor()
        SQL = "INSERT INTO cart(bike_id,user_id,quantity) VALUES(?,?,?)"
        c = conn.cursor()
        c.execute(SQL,[id, user_id, 1])
        conn.commit()
        conn.close()
    return render_template("select_bike.html", bikes = bikes[0], logstatus = session.get('logstatus', None))

@app.route("/login", methods=["GET","POST"])
def login():
    log_status = 'false'
    if session.get('logstatus', None) != "false":
        return redirect(url_for('bikes'))
    else:
        if request.method == "POST":
            user_name = request.form.get("user_name")
            password = request.form.get("password")
            if user_name and password:
                conn = sqlite3.connect('Beamma-Bikes.db')
                c = conn.cursor()
                c.execute("SELECT id, password FROM users WHERE name=?",(user_name,))
                log_user = c.fetchall()
                conn.close()
                if log_user:
                    log_user = log_user[0]
                    log_password = log_user[1]
                    log_user_id = log_user[0]
                    if log_password:
                        log_status = check_password_hash(log_password, password)
                    if log_status is True:
                        session['logstatus'] = log_user_id
                        return redirect(url_for('user'))
                    else:
                        session['logstatus'] = 'false'
                        print("Failed")
                        return redirect(url_for('login'))
                else:
                    return render_template("login.html", logstatus = session.get('logstatus', None))
            else:
                return render_template("login.html", logstatus = session.get('logstatus', None))
        else:
            return render_template("login.html", logstatus = session.get('logstatus', None))

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        user_name = request.form.get("user_name")
        print(user_name)
        hashed_password = generate_password_hash(request.form.get("password"), salt_length=10)
        conn = sqlite3.connect('Beamma-Bikes.db')
        cur = conn.cursor()
        SQL = "INSERT INTO users(name,password) VALUES(?,?)"
        cur.execute(SQL,[user_name, hashed_password])
        conn.commit()
        cur.execute("SELECT id FROM users WHERE name=?",(user_name,))
        user_id = cur.fetchall()
        user_id = user_id[0]
        conn.close()
        session['logstatus'] = user_id[0]
        return redirect(url_for('user'))
    else:
        return render_template("register.html", logstatus = session.get('logstatus', None))

@app.route("/user", methods=["GET", "POST"])
def user():
    if session.get('logstatus', None) == "false":
        return redirect(url_for("bikes"))
    else:
        user_id = session.get('logstatus', None)
        conn = sqlite3.connect('Beamma-Bikes.db')
        c = conn.cursor()
        c.execute("SELECT bikes.name, bikes.price, cart.quantity, cart.id FROM cart INNER JOIN bikes ON cart.bike_id = bikes.id WHERE user_id=?", (user_id,))
        cart = c.fetchall()
        c.execute("SELECT name FROM users WHERE id=?",(user_id,))
        name = c.fetchall()
        name = name[0]
        conn.close()
        price = 0
        quantity = 0
        for i in range(len(cart)):
            bike = cart[i]
            price += bike[1] * bike[2]
            if bike[2] < 1:
                conn = sqlite3.connect('Beamma-Bikes.db')
                c = conn.cursor()
                c.execute("DELETE FROM cart WHERE id = ?",(bike[3],))
                conn.commit()
                conn.close()
                return redirect(url_for("user"))
            quantity += bike[2]
        if request.method == "POST":
            if request.form.get("logout"):
                session['logstatus'] = 'false'
                return redirect(url_for('bikes'))
            else:
                for i in range(len(cart)):
                    cart_id = cart[i]
                    bike_quantity = request.form.get(str(cart_id[3]))
                    print(cart_id[3], bike_quantity)
                    conn = sqlite3.connect('Beamma-Bikes.db')
                    c = conn.cursor()
                    c.execute("UPDATE cart SET quantity = ? WHERE id = ?",(bike_quantity, cart_id[3],))
                    conn.commit()
                    conn.close()
                return(redirect(url_for("user")))
        return render_template("user.html", logstatus = session.get('logstatus', None), cart = cart, name = name[0], price = price, quantity = quantity)

if __name__ == "__main__":
    app.run(debug=True)
