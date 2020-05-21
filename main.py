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
        query = "SELECT name, image, id FROM bikes "
        fcount = 0
        tcount = 0
        ycount = 0
        bracket = ""
        # Requests
        r_polygon = request.form.get('polygon')
        r_trek = request.form.get('trek')
        r_giant = request.form.get('giant')
        r_liv = request.form.get('liv')
        r_enduro = request.form.get('enduro')
        r_trail = request.form.get('trail')
        r_ebike = request.form.get('ebike')
        r_downhill = request.form.get('downhill')
        r_jumper = request.form.get('jumper')
        r_xc = request.form.get('xc')
        twenty = request.form.get('2020')
        nineteen = request.form.get('2019')
        eighteen = request.form.get('2018')
        sort = request.form.get('sort')

        # Add "WHERE" if a filter has been applied
        if r_polygon or r_trek or r_giant or r_liv or r_trail or r_ebike or r_enduro or r_downhill or r_jumper or r_xc or twenty or eighteen or nineteen is not None:
            query += "WHERE ("
            bracket = ") "
        # Check what filters have been applied
        if r_polygon is not None:
            if fcount > 0:
                query += "OR " # Check if "AND" is neccessary
            query += "brand = 1 " # Add Filter
            fcount += 1

        if r_trek is not None:
            if fcount > 0:
                query += "OR " # Check if "AND" is neccessary
            query += "brand = 2 " # Add Filter
            fcount += 1

        if r_giant is not None:
            if fcount > 0:
                query += "OR " # Check if "AND" is neccessary
            query += "brand = 3 " # Add Filter
            fcount += 1

        if r_liv is not None:
            if fcount > 0:
                query += "OR " # Check if "AND" is neccessary
            query += "brand = 4 " # Add Filter
            fcount += 1

        if r_polygon or r_trek or r_giant or r_liv is not None:
            if r_trail or r_ebike or r_enduro or r_downhill or r_jumper or r_xc is not None:
                query += ") AND ("

        if r_trail is not None:
            if tcount > 0:
                query += "OR " # Check if "AND" is neccessary
            query += "type = 3 " # Add Filter
            tcount += 1

        if r_ebike is not None:
            if tcount > 0:
                query += "OR " # Check if "AND" is neccessary
            query += "type = 1 " # Add Filter
            tcount += 1

        if r_enduro is not None:
            if tcount > 0:
                query += "OR " # Check if "AND" is neccessary
            query += "type = 5 " # Add Filter
            tcount += 1

        if r_downhill is not None:
            if tcount > 0:
                query += "OR " # Check if "AND" is neccessary
            query += "type = 4 " # Add Filter
            tcount += 1

        if r_jumper is not None:
            if tcount > 0:
                query += "OR " # Check if "AND" is neccessary
            query += "type = 2 " # Add Filter
            tcount += 1

        if r_xc is not None:
            if tcount > 0:
                query += "OR " # Check if "AND" is neccessary
            query += "type = 6 " # Add Filter
            tcount += 1

        if r_polygon or r_trek or r_giant or r_liv or r_trail or r_ebike or r_enduro or r_downhill or r_jumper or r_xc is not None:
            if twenty or eighteen or nineteen is not None:
                query += ") AND ("

        if twenty is not None:
            if ycount > 0:
                query += "OR "
            query += "year = 2020 "
            ycount += 1

        if nineteen is not None:
            if ycount > 0:
                query += "OR "
            query += "year = 2019 "
            ycount += 1

        if eighteen is not None:
            if ycount > 0:
                query += "OR "
            query += "year = 2018 "
            ycount += 1

        print(sort)
        query += bracket
        query += sort

        print(query) # Debug
        # Connect to databse and preform query
        conn = sqlite3.connect('Beamma-Bikes.db')
        c = conn.cursor()
        c.execute(query)
        bikes = c.fetchall()
        conn.close()
        return render_template("bikes.html", bikes = bikes)

    # Normal Page Loading
    else:

        # Connect to databse and preform query
        conn = sqlite3.connect('Beamma-Bikes.db')
        c = conn.cursor()
        c.execute("SELECT name, image, id FROM Bikes")
        bikes = c.fetchall()
        conn.close()
        return render_template("bikes.html", bikes = bikes)

@app.route("/<id>")
def test(id):
    conn = sqlite3.connect('Beamma-Bikes.db')
    c = conn.cursor()
    c.execute("SELECT bikes.name, bikes.image, bikes.price, bikes.description, brand.name FROM bikes INNER JOIN brand ON bikes.brand = brand.id WHERE bikes.id=?", (id))
    bikes = c.fetchall()
    conn.close()
    return render_template("select_bike.html", bikes = bikes[0])

if __name__ == "__main__":
    app.run(debug=True)
