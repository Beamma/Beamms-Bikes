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
        post_id = request.form.get('Polygon')
        if post_id is not None:
            conn = sqlite3.connect('Beamma-Bikes.db')
            c = conn.cursor()
            c.execute("SELECT name, image FROM Bikes WHERE brand=1")
            bike = c.fetchall()
            conn.close()
            print(post_id)
            return render_template("bikes.html", bike = bike)

if __name__ == "__main__":
    app.run(debug=True)
