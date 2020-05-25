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
        fcount = 0
        tcount = 0
        ycount = 0
        scount = 0
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
        xsmall = request.form.get('XS')
        small = request.form.get('S')
        medium = request.form.get('M')
        large = request.form.get('L')
        xlarge = request.form.get('XL')
        sort = request.form.get('sort')

        # Add "WHERE" if a filter has been applied
        if r_polygon or r_trek or r_giant or r_liv or r_trail or r_ebike or r_enduro or r_downhill or r_jumper or r_xc or twenty or eighteen or nineteen or xsmall or small or medium or large or xlarge is not None:
            query += "WHERE ("
            bracket = ") "

        # Check what filters have been applied
        if r_polygon is not None:
            if fcount > 0:
                query += "OR " # Check if "AND" is neccessary
            query += "bikes.brand = 1 " # Add Filter
            fcount += 1

        if r_trek is not None:
            if fcount > 0:
                query += "OR " # Check if "AND" is neccessary
            query += "bikes.brand = 2 " # Add Filter
            fcount += 1

        if r_giant is not None:
            if fcount > 0:
                query += "OR " # Check if "AND" is neccessary
            query += "bikes.brand = 3 " # Add Filter
            fcount += 1

        if r_liv is not None:
            if fcount > 0:
                query += "OR " # Check if "AND" is neccessary
            query += "bikes.brand = 4 " # Add Filter
            fcount += 1

        if r_polygon or r_trek or r_giant or r_liv is not None:
            if r_trail or r_ebike or r_enduro or r_downhill or r_jumper or r_xc is not None:
                query += ") AND ("

        if r_trail is not None:
            if tcount > 0:
                query += "OR " # Check if "AND" is neccessary
            query += "bikes.type = 3 " # Add Filter
            tcount += 1

        if r_ebike is not None:
            if tcount > 0:
                query += "OR " # Check if "AND" is neccessary
            query += "bikes.type = 1 " # Add Filter
            tcount += 1

        if r_enduro is not None:
            if tcount > 0:
                query += "OR " # Check if "AND" is neccessary
            query += "bikes.type = 5 " # Add Filter
            tcount += 1

        if r_downhill is not None:
            if tcount > 0:
                query += "OR " # Check if "AND" is neccessary
            query += "bikes.type = 4 " # Add Filter
            tcount += 1

        if r_jumper is not None:
            if tcount > 0:
                query += "OR " # Check if "AND" is neccessary
            query += "bikes.type = 2 " # Add Filter
            tcount += 1

        if r_xc is not None:
            if tcount > 0:
                query += "OR " # Check if "AND" is neccessary
            query += "bikes.type = 6 " # Add Filter
            tcount += 1

        if r_polygon or r_trek or r_giant or r_liv or r_trail or r_ebike or r_enduro or r_downhill or r_jumper or r_xc is not None:
            if twenty or eighteen or nineteen is not None:
                query += ") AND ("

        if twenty is not None:
            if ycount > 0:
                query += "OR "
            query += "bikes.year = 2020 "
            ycount += 1

        if nineteen is not None:
            if ycount > 0:
                query += "OR "
            query += "bikes.year = 2019 "
            ycount += 1

        if eighteen is not None:
            if ycount > 0:
                query += "OR "
            query += "bikes.year = 2018 "
            ycount += 1

        if r_polygon or r_trek or r_giant or r_liv or r_trail or r_ebike or r_enduro or r_downhill or r_jumper or r_xc or twenty or eighteen or nineteen is not None:
            if xsmall or small or medium or large or xlarge is not None:
                query += ") AND ("

        if xsmall is not None:
            if scount > 0:
                query += "OR "
            query += "bikes_sizes.sid = 1 "
            scount += 1

        if small is not None:
            if scount > 0:
                query += "OR "
            query += "bikes_sizes.sid = 2 "
            scount += 1

        if medium is not None:
            if scount > 0:
                query += "OR "
            query += "bikes_sizes.sid = 3 "
            scount += 1

        if large is not None:
            if scount > 0:
                query += "OR "
            query += "bikes_sizes.sid = 4 "
            scount += 1

        if xlarge is not None:
            if scount > 0:
                query += "OR "
            query += "bikes_sizes.sid = 5 "
            scount += 1

        query += bracket
        query += sort
        print (query)

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
