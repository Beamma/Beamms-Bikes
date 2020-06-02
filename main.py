from flask import Flask, redirect, url_for, render_template, request
import sqlite3

app = Flask(__name__)

# Home Page
@app.route('/')
def home():
    return render_template("home.html")

# Bikes Page
@app.route('/bikes', methods=["GET","POST"])
def bikes():
    conn = sqlite3.connect('Beamma-Bikes.db')
    c = conn.cursor()
    c.execute("SELECT id, name FROM brand")
    brands = c.fetchall()
    # brands.append("brands")
    c.execute("SELECT id, name FROM type")
    types = c.fetchall()
    # types.append("type")
    c.execute("SELECT DISTINCT year FROM bikes ORDER BY year DESC")
    years = c.fetchall()
    # years.append("year")
    c.execute("SELECT id, size FROM sizes ORDER BY id ASC")
    sizes = c.fetchall()
    # sizes.append("sid")
    # filter_options = [brands, types, years, sizes]
    filter_options = dict(
        brand=brands,
        type=types,
        year=years,
        sid=sizes,
    )
    # print(filter_options)

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
        return render_template("bikes.html", bikes = bikes, filter_options = filter_options)

	# Normal Page Loading
    else:

		# Connect to databse and preform query
        conn = sqlite3.connect('Beamma-Bikes.db')
        c = conn.cursor()
        c.execute("SELECT name, image, id FROM Bikes")
        bikes = c.fetchall()
        conn.close()
        return render_template("bikes.html", bikes = bikes, filter_options = filter_options)

@app.route("/bikes/<id>")
def bike(id):
    conn = sqlite3.connect('Beamma-Bikes.db')
    c = conn.cursor()
    c.execute("SELECT bikes.name, bikes.image, bikes.price, bikes.description, brand.name FROM bikes INNER JOIN brand ON bikes.brand = brand.id WHERE bikes.id=?", (id,))
    bikes = c.fetchall()
    conn.close()

    return render_template("select_bike.html", bikes = bikes[0])

if __name__ == "__main__":
    app.run(debug=True)
