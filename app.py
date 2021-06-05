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


# Resource: Adding comments best practices -
# https://www.askpython.com/python/python-comments


@app.route('/')
def home():
    """
    Function to load the homepage
    Pull User's username from MongoDB
    """
    return render_template('pages/home.html')


@app.route('/register', methods=["GET", "POST"])
def register():
    """
    Allows user to register on the website
    Checks if username already exists in Database
    Adds blank user profile data to MongoDB
    Redirects user to Dashboard
    """
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Sorry, this username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "image": "",
            "gender": "",
            "dob": "",
            "height": "",
            "height_metric": ""
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
    Ensure hashed password matches user input
    Redirect to login if no username/password match
    """
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(
                    request.form.get("username")))
                return redirect(url_for(
                    "dashboard", username=session["user"]))

            else:
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("pages/user-authentication.html")


@app.route("/dashboard/<username>", methods=["GET", "POST"])
def dashboard(username):
    """
    Take the session user's username from database
    Set variable username equal to user's username
    Set variable user_id equal to user's _id
    Set variable profiles equal to user's username
    Set variable logs equal to user's username
    """
    user = mongo.db.users.find_one({"username": session["user"]})
    username = user["username"]
    user_id = user["_id"]
    profiles = mongo.db.users.find({"username": user["username"]})
    logs = mongo.db.logs.find({"username": user["username"]})
    if session["user"]:
        return render_template(
            "pages/dashboard.html", username=username,
            profiles=profiles, logs=logs, user_id=user_id)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    """
    Logout function to remove user from session cookies
    """
    flash("You have successfully logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route('/patientprofile/<username>', methods=["GET", "POST"])
def patientprofile(username):
    """
    Post profile form data to MongoDB user document
    Allow user to create one profile
    Link MongoDB height_metric and gender data to form dropdowns
    """
    if request.method == "POST":
        user = mongo.db.users
        # Resource: Set Operator -
        # https://docs.mongodb.com/manual/reference/operator/update/set/
        user.update(
            {"username": session["user"]},
            {"$set":
                {
                    "image": request.form.get("patient-image"),
                    "gender": request.form.get("patient-gender"),
                    "dob": request.form.get("patient-dob"),
                    "height": request.form.get("patient-height"),
                    "height_metric": request.form.get("height_metric")
                }}
        )
        flash("Profile Updated")
        return redirect(
            url_for("dashboard", username=session["user"]))

    if request.method == "POST":
        user.count()
        return redirect(
            url_for("dashboard", username=session["user"]))

    user = mongo.db.users.find_one({"username": session["user"]})
    image = user["image"]
    username = user["username"]
    height = user["height"]
    dob = user["dob"]
    height_metric = mongo.db.height_metric.find().sort("height_metric", 1)
    gender = mongo.db.gender.find().sort("gender", 1)
    return render_template(
        "pages/patientprofile.html",
        gender=gender, height_metric=height_metric,
        username=username, height=height, dob=dob, image=image)


@app.route("/delete_profile/<user_id>")
def delete_profile(user_id):
    mongo.db.users.remove({"_id": ObjectId()})
    flash("Profile Successfully Deleted")
    return redirect(
        url_for("dashboard", username=session["user"]))


@app.route('/patientlog', methods=["GET", "POST"])
def patientlog():
    """
    Post log form data to MongoDB
    Link MongoDB status and weight_metric data to form dropdowns
    """
    if request.method == "POST":
        log = {
            "username": session["user"],
            "log_date": request.form.get("log-date"),
            "status": request.form.get("patient-status"),
            "weight": request.form.get("patient-weight"),
            "weight_metric": request.form.get("weight_metric"),
            "symptoms": request.form.get("patient-symptoms")
        }
        mongo.db.logs.insert_one(log)
        flash("Log Created")
        return redirect(
            url_for("dashboard", username=session["user"]))

    user = mongo.db.users.find_one({"username": session["user"]})
    username = user["username"]
    weight_metric = mongo.db.weight_metric.find().sort("weight_metric", 1)
    status = mongo.db.status.find().sort("status", 1)
    return render_template(
        "pages/patientlog.html",
        status=status, weight_metric=weight_metric, username=username)


@app.route("/editlog/<log_id>", methods=["GET", "POST"])
def editlog(log_id):
    """
    Function to edit existing log data
    """
    if request.method == "POST":
        submit = {
            "username": session["user"],
            "log_date": request.form.get("log-date"),
            "status": request.form.get("patient-status"),
            "weight": request.form.get("patient-weight"),
            "weight_metric": request.form.get("weight_metric"),
            "symptoms": request.form.get("patient-symptoms")
        }
        mongo.db.logs.update({"_id": ObjectId(log_id)}, submit)
        flash("Log Successfully Updated")

    user = mongo.db.users.find_one({"username": session["user"]})
    username = user["username"]
    log = mongo.db.logs.find_one({"_id": ObjectId(log_id)})
    weight_metric = mongo.db.weight_metric.find().sort("weight_metric", 1)
    status = mongo.db.status.find().sort("status", 1)
    return render_template(
        "pages/editlog.html",
        status=status, weight_metric=weight_metric, log=log, username=username)


@app.route("/delete_log/<log_id>")
def delete_log(log_id):
    """
    Function to remove log from database
    """
    mongo.db.logs.remove({"_id": ObjectId(log_id)})
    flash("Log Successfully Deleted")
    return redirect(
        url_for("dashboard", username=session["user"]))


@app.errorhandler(404)
def page_not_found(e):
    """
    Function for custom 404 error page
    """
    # Resource: Linking to 404 page -
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


"""
@app.route("/profile/<user_id>", methods=["GET", "POST"])
def profile(user_id):
    user_id = mongo.db.users.find_one(
        {"user": session["user"]})["_id"]
    return render_template("/pages/dashboard.html", user_id=user_id)
"""

"""
@app.route('/patientprofile/<username>', methods=["GET", "POST"])
def patientprofile(username):
    Post profile form data to MongoDB user document
    Allow user to create one profile
    Link MongoDB height_metric and gender data to form dropdowns
    if request.method == "POST":
        user = mongo.db.users
        # Resource: Set Operator -
        # https://docs.mongodb.com/manual/reference/operator/update/set/
        user.update(
            {"username": session["user"]},
            {"$set":
                {
                    "image": request.form.get("patient-image"),
                    "gender": request.form.get("patient-gender"),
                    "dob": request.form.get("patient-dob"),
                    "height": request.form.get("patient-height"),
                    "height_metric": request.form.get("height_metric")
                }}
        )
        flash("Profile Updated")
        return redirect(
            url_for("dashboard", username=session["user"]))

    if request.method == "POST":
        user.count()
        return redirect(
            url_for("dashboard", username=session["user"]))

    user = mongo.db.users.find_one({"username": session["user"]})
    username = user["username"]
    height_metric = mongo.db.height_metric.find().sort("height_metric", 1)
    gender = mongo.db.gender.find().sort("gender", 1)
    return render_template(
        "pages/patientprofile.html",
        gender=gender, height_metric=height_metric, username=username)
"""
