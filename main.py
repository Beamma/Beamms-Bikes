from flask import Flask, redirect, url_for, render_template, request
import sqlite3

app = Flask(__name__)

@app.route('/home')
def home():
    return render_template("home.html")

@app.route('/bikes', methods=["GET","POST"])
def bikes():

    # FILTER SYSTEM
    if request.method == 'POST':

        # VARIABLES
        t_count = 0
        b_count = 0
        f_count = 0
        wheel = ""
        s_filter = ""
        where = ""
        one_b = ""
        two_b = ""
        one_t = ""
        two_t = ""
        polygon = ""
        trek = ""
        enduro =""

        # REQUESTS
        r_polygon = request.form.get('polygon')
        r_trek = request.form.get('trek')
        r_enduro = request.form.get('enduro')

        # CHECK FILTERS
        if r_polygon is not None:
            where = " WHERE"
            polygon = "1"
            b_count += 1

        if r_trek is not None:
            where = " WHERE"
            trek ="2"
            b_count += 1

        if r_enduro is not None:
            where = " WHERE"
            enduro = "5"
            t_count += 1
            if b_count > 0:
                f_count += 1


        # ADDS "AND" IF NECCESARY
        if b_count > 0:
            one_b = " brand ="

        if b_count > 1:
            two_b = " or "

        if f_count > 0:
            s_filter = " AND"

        if f_count < 1:
            s_filter = ""

        if t_count > 0:
            one_t = " type ="

        if t_count > 1:
            two_t = " or "

        # CONNECT TO DATA BASE AND RUN BUILT QUERY
        conn = sqlite3.connect('Beamma-Bikes.db')
        c = conn.cursor()
        print("SELECT name, image FROM Bike" + where + one_b + polygon + two_b + trek + s_filter + one_t + enduro) # DEBUG
        c.execute("SELECT name, image FROM Bikes" + where + one_b + polygon + two_b + trek + s_filter + one_t + enduro)
        bike = c.fetchall()
        conn.close()
        return render_template("bikes.html", bike = bike)

    # BASIC PAGE LOADING
    else:
        conn = sqlite3.connect('Beamma-Bikes.db')
        c = conn.cursor()
        c.execute("SELECT name, image FROM Bikes")
        bike = c.fetchall()
        conn.close()
        return render_template("bikes.html", bike = bike)

if __name__ == "__main__":
    app.run(debug=True)
