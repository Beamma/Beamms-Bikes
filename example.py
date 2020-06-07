from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

    def set_password(self, password):
        # hash the password
        hashed_password = password + "!!!"
        self.password = hashed_password


# create a new user
new_user = User(user_name="hanan")
# new_user.password = "abc" # dont do this use set_password
new_user.set_password("abc")
db.session.add(new_user) # add the new user to the session
db.session.commit() # commit

# get all users
users = User.query.all() # get all users
user = User.query.get(1)
user_hanan = User.query.filter(Us)
