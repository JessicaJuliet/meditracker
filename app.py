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
    """
    Allows user to register on the website
    Checks if username already exists in Database
    Puts new user into session cookie
    Redirects user to dashboard
    """
    if request.method == "POST":
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

        session["user"] = request.form.get("username").lower()
        flash("You have successfully registered")
        return redirect(url_for("dashboard", username=session["user"]))

    return render_template("pages/user-authentication.html", register=True)


@app.route('/login', methods=["GET", "POST"])
def login():
    """
    Check if username exists in database
    """
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # Ensure hashed password matches user input
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(
                    request.form.get("username")))
                return redirect(url_for(
                    "dashboard", username=session["user"]))

            else:
                # Invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # Username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("pages/user-authentication.html")


@app.route("/dashboard/<username>", methods=["GET", "POST"])
def dashboard(username):
    # Grab the session user's username from database
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    return render_template("pages/dashboard.html", username=username)

    if session["user"]:
        return render_template("pages/dashboard.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # Remove user from session cookies
    flash("You have successfully logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route('/log')
def log():
    """
    Add/edit log
    """
    return render_template("pages/log.html")


@app.route('/update_profile', methods=["GET", "POST"])
def update_profile():
    if request.method == "POST":
        profile = {
            "username": session["user"],
            "image": request.form.get("patient-image"),
            "gender": request.form.get("patient-gender"),
            "dob": request.form.get("patient-dob"),
            "height": request.form.get("patient-height"),
            "height-metric": request.form.get("height-metric")
        }
        mongo.db.profiles.insert_one(profile)
        flash("Profile Updated")
        return redirect(
            url_for("dashboard", username=session["user"]))

    height_metric = mongo.db.height_metric.find().sort("height_metric", 1)
    gender = mongo.db.gender.find().sort("gender", 1)
    return render_template(
        "pages/update_profile.html",
        gender=gender, height_metric=height_metric)


@app.errorhandler(404)
def page_not_found(e):
    # Resource:
    # https://flask.palletsprojects.com/en/2.0.x/errorhandling/?highlight=404
    return render_template("pages/404.html"), 404


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
