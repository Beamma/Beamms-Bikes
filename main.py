from flask import Flask, redirect, url_for, render_template, request
import sqlite3

app = Flask(__name__)

@app.route('/home')
def home():
    return render_template("home.html")

@app.route('/bikes')
def bikes():
    conn = sqlite3.connect('Beamma-Bikes.db')
    c = conn.cursor()
    c.execute("SELECT name, image FROM Bikes")
    bike = c.fetchall()
    conn.close()
    return render_template("bikes.html", bike = bike)

@app.route('/bikes', methods=["GET","POST"])
def filtered():
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

        # REQUESTS
        polygon = request.form.get('polygon')
        trek = request.form.get('trek')
        type = request.form.get('type')

        # CHECK FILTERS
        if polygon is not None:
            where = " WHERE"
            polygon = "1"
            b_count += 1

        if trek is not None:
            where = " WHERE"
            trek ="1"
            b_count += 1

        if type is not None:
            where = " WHERE"
            type = "5"
            t_count += 1


        # ADDS "AND" IF NECCESARY
        if b_count > 0:
            one_b = " brand ="
            f_count += 1

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
        conn = sqlite3.connect('Beamma-Bikes.db')
        c = conn.cursor()
        c.execute("SELECT name, image FROM Bikes")
        bike = c.fetchall()
        conn.close()
        return render_template("bikes.html", bike = bike)

if __name__ == "__main__":
    app.run(debug=True)
