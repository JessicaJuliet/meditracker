import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


"""
@app.route("/")
@app.route("/get_patients")
def get_patients():
    patients = mongo.db.patients.find()
    return render_template("patients.html", patients=patients)
"""


@app.route('/')
def home():
    """
    Function to load the homepage
    """
    return render_template('pages/home.html')


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Check if username already exisits in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        if existing_user:
            flash("Sorry, this username already exists")
            return redirect(url_for("register"))
        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("You have successfully registered")
    return render_template("pages/register.html")


@app.route('/facebook')
def facebook():
    """
    Function to load the Facebook
    """
    return redirect("https://www.facebook.com")


@app.route('/instagram')
def instagram():
    """
    Function to load the Instagram
    """
    return redirect("https://www.instagram.com")


@app.route('/linkedin')
def linkedin():
    """
    Function to load the Linkedin
    """
    return redirect("https://www.linkedin.com")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
# update to debug=False prior to actual
# deployment of project submission
