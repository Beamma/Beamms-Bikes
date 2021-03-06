from flask import Flask, redirect, url_for, render_template, request, session
import sqlite3, os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'super secret key'

# Home Page
@app.route('/')
def home():
    logstatus = 'false'
    return render_template("home.html", logstatus = session.get('logstatus', None), adminstatus = session.get('adminstatus', None))

# Bikes Page
@app.route('/bikes', methods=["GET","POST"])
def bikes():
    logstatus = 'false' # Set log_status To False By Default

    # Import Filter Options From Data Base
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
        query = "SELECT DISTINCT bikes.name, bikes.image, bikes.id, bikes.price FROM bikes INNER JOIN bikes_sizes ON bikes_sizes.bid = bikes.id "
        parms = []
        filters = []
        search = request.form.get("search")
        print("search:", search)

        # Build Query
        for key in request.form:
            if key == "search": continue
            if key == "sort": continue # Ignore Sort
            values = request.form.getlist(key)
            column = "bikes_sizes." + key if key == "sid" else 'bikes.' + key
            filters.append(f"{column} IN (" + ", ".join(['?']*len(values)) + ") ")
            parms += values
        if filters:
            query += " WHERE " + " AND ".join(filters)
        query += request.form.getlist("sort")[0]

        # Search Bikes
        conn = sqlite3.connect('Beamma-Bikes.db')
        c = conn.cursor()
        if search != "":
            query = "SELECT DISTINCT bikes.name, bikes.image, bikes.id, bikes.price FROM bikes WHERE bikes.name LIKE '%" + search + "%' "
            c.execute(query)
            bikes = c.fetchall()
            conn.close()

        # Execute Query
        else:
            print("filter")
            c.execute(query, parms)
            bikes = c.fetchall()
            conn.close()
        return render_template("bikes.html", bikes = bikes, filter_options = filter_options, logstatus = session.get('logstatus', None), adminstatus = session.get('adminstatus', None))

	# Normal Page Loading
    else:

		# Connect to databse and preform query
        conn = sqlite3.connect('Beamma-Bikes.db')
        c = conn.cursor()
        c.execute("SELECT name, image, id, price FROM Bikes")
        bikes = c.fetchall()
        conn.close()
        return render_template("bikes.html", bikes = bikes, filter_options = filter_options, logstatus = session.get('logstatus', None), adminstatus = session.get('adminstatus', None))

# Singular Bike Routes
@app.route("/bikes/<int:id>", methods=["GET", "POST"])
def bike(id):
    logstatus = 'false' # Set logstatus To False By Default
    status = "" # Create Empty Status

    # Bike Infor For Display
    conn = sqlite3.connect('Beamma-Bikes.db')
    c = conn.cursor()
    c.execute("SELECT bikes.name, bikes.image, bikes.price, bikes.description, brand.name FROM bikes INNER JOIN brand ON bikes.brand = brand.id WHERE bikes.id=?", (id,))
    bikes = c.fetchall()
    c.execute ("SELECT sizes.size, sizes.id FROM bikes_sizes INNER JOIN sizes ON sid = id WHERE bid = ?", (id,))
    bike_sizes = c.fetchall()
    conn.close()

    # Person Added Bike To Cart
    if request.method == "POST":
        if session.get('logstatus', None) != "false":
            quantity = int(request.form.get("quantity"))
            size = int(request.form.get("size"))
            user_id = session.get('logstatus', None)
            conn = sqlite3.connect('Beamma-Bikes.db')
            c = conn.cursor()

            # Select Shop Quantity For Bike
            c.execute("SELECT bikes_sizes.quantity FROM bikes_sizes WHERE bid = ? AND sid = ?", (id, size,))
            shop_quantity = c.fetchall()[0]
            shop_quantity = int(shop_quantity[0])

            # Check If Quantity Is Sufficiant
            if shop_quantity == 0:
                status = "OOS"
                return render_template("select_bike.html", bikes = bikes[0], logstatus = session.get('logstatus', None), status = status, bike_sizes = bike_sizes, adminstatus = session.get('adminstatus', None))
            if shop_quantity < quantity:
                status = "Low_Stock"
                return render_template("select_bike.html", bikes = bikes[0], logstatus = session.get('logstatus', None), status = status, bike_sizes = bike_sizes, adminstatus = session.get('adminstatus', None))

            # Update Shop Quantity
            new_shop_quantity = shop_quantity - quantity
            c.execute("UPDATE bikes_sizes SET quantity = ? WHERE bikes_sizes.bid = ? AND bikes_sizes.sid = ?", (new_shop_quantity, id, size,))
            conn.commit()
            cart = c.execute("SELECT cart.bike_id, cart.user_id, cart.quantity, cart.size FROM cart")
            cart = cart.fetchall()

            # Add Quantity Of Bikes To Exisiting Quantity In Cart
            for cart_item in cart:
                if cart_item[0] == id and cart_item[1] == user_id and cart_item[3] == size:
                    bike_quantity = cart_item[2] + quantity
                    c.execute("UPDATE cart SET quantity = ? WHERE cart.bike_id = ? AND cart.user_id = ? AND cart.size = ?",(bike_quantity, id, user_id, size,))
                    conn.commit()
                    status = "Worked"
                    break

            # Otherwise Add To Cart As Normal
            else:
                SQL = "INSERT INTO cart(bike_id,user_id,quantity,size) VALUES(?,?,?,?)"
                c.execute(SQL,[id, user_id, quantity,size])
            conn.commit()
            conn.close()
            status = "Worked"
            return render_template("select_bike.html", bikes = bikes[0], logstatus = session.get('logstatus', None), status = status, bike_sizes = bike_sizes, adminstatus = session.get('adminstatus', None))
        else:
            status = "Failed"
            return render_template("select_bike.html", bikes = bikes[0], logstatus = session.get('logstatus', None), status = status, bike_sizes = bike_sizes, adminstatus = session.get('adminstatus', None))
    return render_template("select_bike.html", bikes = bikes[0], logstatus = session.get('logstatus', None),bike_sizes = bike_sizes, adminstatus = session.get('adminstatus', None))

# Login Page
@app.route("/login", methods=["GET","POST"])
def login():
    log_status = 'false'

    # Only Allow Access To Non Users
    if session.get('logstatus', None) != "false":
        return redirect(url_for('bikes'))
    else:
        if request.method == "POST":

            # Retreive User And Password And Check Against Exisiting Accounts To See If Match
            user_name = request.form.get("user_name")
            password = request.form.get("password")
            if user_name and password:
                conn = sqlite3.connect('Beamma-Bikes.db')
                c = conn.cursor()
                c.execute("SELECT id, password, admin FROM users WHERE name=?",(user_name,))
                log_user = c.fetchall()
                conn.close()
                if log_user:
                    log_user = log_user[0]
                    log_password = log_user[1]
                    log_user_id = log_user[0]
                    log_admin = log_user[2]
                    if log_password:
                        log_status = check_password_hash(log_password, password)

                    # If User Has Logged In Use Sessions And Create Status To Such
                    if log_status is True:
                        session['logstatus'] = log_user_id
                        session['adminstatus'] =  log_admin
                        return redirect(url_for('user'))

                    # Otherise Dont Allow Access And Redirect
                    else:
                        session['logstatus'] = 'false'
                        print("Failed")
                        return redirect(url_for('login'))
                else:
                    return render_template("login.html", logstatus = session.get('logstatus', None), adminstatus = session.get('adminstatus', None))
            else:
                return render_template("login.html", logstatus = session.get('logstatus', None), adminstatus = session.get('adminstatus', None))
        else:
            return render_template("login.html", logstatus = session.get('logstatus', None), adminstatus = session.get('adminstatus', None))

# Register Page
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        session['logstatus'] = 'false'

        # Retreive User And Password, Hash Password
        user_name = request.form.get("user_name")
        hashed_password = generate_password_hash(request.form.get("password"), salt_length=10)
        email = request.form.get("email")
        conn = sqlite3.connect('Beamma-Bikes.db')
        cur = conn.cursor()
        cur.execute("SELECT name, email FROM users")
        existing_info = cur.fetchall()

        # Check That Info Input Is Unique
        for user_info in existing_info:
            if user_name == user_info[0]:
                status = "Username Already In Use"
                session['logstatus'] = 'false'
                return render_template("register.html", logstatus = session.get('logstatus', None), status = status, adminstatus = session.get('adminstatus', None))
            if email == user_info[1]:
                status = "Email Already In Use"
                session['logstatus'] = 'false'
                return render_template("register.html", logstatus = session.get('logstatus', None), status = status, adminstatus = session.get('adminstatus', None))

        # If Input Is Unique Add To Data Base
        status = ""
        SQL = "INSERT INTO users(name,password,email) VALUES(?,?,?)"
        cur.execute(SQL,[user_name, hashed_password, email])
        conn.commit()
        cur.execute("SELECT id FROM users WHERE name=?",(user_name,))
        user_id = cur.fetchall()
        conn.close()
        user_id = user_id[0]
        session['logstatus'] = user_id[0]

        return redirect(url_for('user'))
    else:
        return render_template("register.html", logstatus = session.get('logstatus', None), adminstatus = session.get('adminstatus', None))

# User Route
@app.route("/user", methods=["GET", "POST"])
def user():

    # Make Sure User Is Logged In
    if session.get('logstatus', None) == "false":
        return redirect(url_for("bikes"))

    # Otherwise Select Name And Items In Cart In Order To View
    else:
        user_id = session.get('logstatus', None)
        conn = sqlite3.connect('Beamma-Bikes.db')
        c = conn.cursor()
        c.execute("SELECT bikes.name, bikes.price, cart.quantity, cart.id, cart.user_id, sizes.size FROM cart INNER JOIN bikes ON cart.bike_id = bikes.id INNER JOIN sizes ON cart.size = sizes.id WHERE user_id=?", (user_id,))
        cart = c.fetchall()
        c.execute("SELECT name FROM users WHERE id=?",(user_id,))
        name = c.fetchall()
        name = name[0]
        conn.close()

        # Calculate Total Price And Quantity
        price = 0
        quantity = 0
        for i in range(len(cart)):
            bike = cart[i]
            quantity += bike[2]
            price += bike[1] * bike[2]

            # Delete Bikes Where Quantity = 0
            if bike[2] < 1:
                conn = sqlite3.connect('Beamma-Bikes.db')
                c = conn.cursor()
                c.execute("DELETE FROM cart WHERE id = ?",(bike[3],))
                conn.commit()
                conn.close()
                return redirect(url_for("user"))

        if request.method == "POST":

            # Log Out User
            if request.form.get("logout"):
                session['logstatus'] = 'false'
                session['adminstatus'] = 0
                return redirect(url_for('bikes'))

            # Otherwise Update Bike Quantity
            else:
                for i in range(len(cart)):
                    cart_id = cart[i]
                    bike_quantity = request.form.get(str(cart_id[3]))
                    conn = sqlite3.connect('Beamma-Bikes.db')
                    c = conn.cursor()
                    c.execute("UPDATE cart SET quantity = ? WHERE id = ?",(bike_quantity, cart_id[3],))
                    conn.commit()
                    conn.close()
                return(redirect(url_for("user")))
        return render_template("user.html", logstatus = session.get('logstatus', None), cart = cart, name = name[0], price = price, quantity = quantity, adminstatus = session.get('adminstatus', None))

# Admin Route
@app.route("/admin", methods=["GET", "POST"])
def admin():

    # Check If User Logged in
    if session.get('logstatus', None) == "false":
        return redirect(url_for("bikes"))

    # Check And Set Admin Status Of User
    else:
        user_id = session.get('logstatus', None)
        conn = sqlite3.connect('Beamma-Bikes.db')
        c = conn.cursor()
        c.execute("SELECT name, admin FROM users WHERE id=?", (user_id,))
        user_admin = c.fetchall()
        conn.commit()
        conn.close()

        user_admin  = user_admin [0]
        user_name = user_admin[0]
        user_admin  = user_admin[1]

        # If User Is Admin Allow Access
        if user_admin == 1:

            # Select All Data Base Fields In Order To Upload On Bikes To DB
            conn = sqlite3.connect('Beamma-Bikes.db')
            c = conn.cursor()
            c.execute("SELECT id, name FROM brand")
            brands = c.fetchall()
            c.execute("SELECT id, name FROM type")
            types = c.fetchall()
            c.execute("SELECT id, size FROM wheel_sizes")
            wheels = c.fetchall()
            c.execute("SELECT id, gender FROM genders")
            genders = c.fetchall()
            c.execute("SELECT id, size FROM sizes")
            sizes = c.fetchall()
            c.execute("SELECT id, name FROM bikes")
            bikes = c.fetchall()
            conn.commit()
            conn.close()
            if request.method == "POST":

                # Check To See If User Wants To Delete Bike From DB
                delete = request.form.get("delete")
                if delete != "default":
                    conn = sqlite3.connect('Beamma-Bikes.db')
                    c = conn.cursor()
                    c.execute("DELETE FROM bikes WHERE id = ?",(delete,))
                    conn.commit()
                    conn.close()

                # Otherwise Request All Info For Newly Created Bike
                else:
                    name = request.form.get("name")
                    brand = int(request.form.get("brand"))
                    type = int(request.form.get("type"))
                    price = int(request.form.get("price"))
                    year = int(request.form.get("year"))
                    wheel = request.form.get("wheels")
                    description = request.form.get("description")
                    gender = request.form.get("genders")
                    desc = request.form.get("description")

                    # Upload Photo To Folder
                    img_file = request.files["image"]
                    img_file.save(os.path.join("static/", img_file.filename))
                    img_location = "static/" + img_file.filename

                    # Insert Bike Into Data Base
                    conn = sqlite3.connect('Beamma-Bikes.db')
                    c = conn.cursor()
                    SQL = "INSERT INTO bikes(name,type,price,brand,year,wheel_size,image,description,gender) VALUES(?,?,?,?,?,?,?,?,?)"
                    c.execute(SQL,[name, type, price, brand, year, wheel, img_location, description, gender])
                    conn.commit()

                    # Get Bid In Order To Insert Size Into Data Base
                    c.execute("SELECT id FROM bikes WHERE name = ?", (name,))
                    bike_id = c.fetchall()
                    bike_id = bike_id[0]

                    # Insert Sizes Into Data Base
                    size_id = []
                    for i in range(len(sizes)):
                        SQL = "INSERT INTO bikes_sizes(bid,sid,quantity) VALUES(?,?,?)"
                        c.execute(SQL,[bike_id[0], i+1, request.form.get(str(i+1))])
                        conn.commit()
                    conn.close()
                return render_template("admin.html", name = user_name, logstatus = session.get('logstatus', None), adminstatus = session.get('adminstatus', None), brands = brands, types = types, wheels = wheels, genders = genders, sizes = sizes, bikes = bikes)
            else:
                return render_template("admin.html", name = user_name, logstatus = session.get('logstatus', None), adminstatus = session.get('adminstatus', None), brands = brands, types = types, wheels = wheels, genders = genders, sizes = sizes, bikes = bikes)

        else:
            return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
