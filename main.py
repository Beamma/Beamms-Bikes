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
			filters.append("{} IN (" + ", ".join(['{}']*len(values)) + ") ")
			if key == "sid":
				parms.append("bikes_sizes." + key)
				parms += values
			else:
				parms.append('bikes.' + key)
				parms += values
		if filters:
			query += " WHERE " + "AND ".join(filters)
		query += request.form.getlist("sort")[0]

		# Execute Query
		conn = sqlite3.connect('Beamma-Bikes.db')
		c = conn.cursor()
		c.execute(query.format(*parms))
		bikes = c.fetchall()
		c.execute("SELECT id, name FROM brand")
		brands = c.fetchall()
		c.execute("SELECT id, name FROM type")
		types = c.fetchall()
		c.execute("SELECT DISTINCT year FROM bikes ORDER BY year DESC")
		years = c.fetchall()
		c.execute("SELECT id, size FROM sizes ORDER BY id ASC")
		sizes = c.fetchall()
		conn.close()
		return render_template("bikes.html", bikes = bikes, brands = brands, types = types, years = years, sizes = sizes)

	# Normal Page Loading
	else:

		# Connect to databse and preform query
		conn = sqlite3.connect('Beamma-Bikes.db')
		c = conn.cursor()
		c.execute("SELECT name, image, id FROM Bikes")
		bikes = c.fetchall()
		c.execute("SELECT id, name FROM brand")
		brands = c.fetchall()
		c.execute("SELECT id, name FROM type")
		types = c.fetchall()
		c.execute("SELECT DISTINCT year FROM bikes ORDER BY year DESC")
		years = c.fetchall()
		c.execute("SELECT id, size FROM sizes ORDER BY id ASC")
		sizes = c.fetchall()
		conn.close()
		return render_template("bikes.html", bikes = bikes, brands = brands, types = types, years = years, sizes = sizes)

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
