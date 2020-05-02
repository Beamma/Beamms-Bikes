from flask import Flask, redirect, url_for, render_template, request
import sqlite3

app = Flask(__name__)

# Home Page
@app.route('/home')
def home():
    return render_template("home.html")

# Bikes Page
@app.route('/bikes', methods=["GET","POST"])
def bikes():

    # FILTER SYSTEM
    if request.method == 'POST':

        # Variables
        query = "SELECT name, image FROM bikes "
        fcount = 0

        # Requests
        r_polygon = request.form.get('polygon')
        r_trek = request.form.get('trek')
        r_enduro = request.form.get('enduro')

        # Add "WHERE" if a filter has been applied
        if r_polygon or r_trek or r_enduro is not None:
            query += "WHERE "

        # Check what filters have been applied
        if r_polygon is not None:
            if fcount > 0:
                query += "AND " # Check if "AND" is neccessary
            query += "brand = 1 " # Add Filter
            fcount += 1

        if r_trek is not None:
            if fcount > 0:
                query += "AND " # Check if "AND" is neccessary
            query += "brand = 2 " # Add Filter
            fcount += 1

        if r_enduro is not None:
            if fcount > 0:
                query += "AND " # Check if "AND" is neccessary
            query += "type = 5 " # Add Filter
            fcount += 1

        print(query) # Debug

        # Connect to databse a preform query
        conn = sqlite3.connect('Beamma-Bikes.db')
        c = conn.cursor()
        c.execute(query)
        bike = c.fetchall()
        conn.close()
        return render_template("bikes.html", bike = bike)

    # Normal Page Loading
    else:

        # Connect to databse a preform query
        conn = sqlite3.connect('Beamma-Bikes.db')
        c = conn.cursor()
        c.execute("SELECT name, image FROM Bikes")
        bike = c.fetchall()
        conn.close()
        return render_template("bikes.html", bike = bike)

if __name__ == "__main__":
    app.run(debug=True)
