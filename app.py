from flask import Flask, render_template, request, flash, session, redirect, url_for
from pymongo import Connection
from search import search_operation
from utils import authenticate, create_account, register_user
import hashlib, uuid
import random
import json
from functools import wraps

app = Flask(__name__)

## mongo 
conn = Connection()
db = conn['users']


def auth(page):
    def decorate(f):
        @wraps(f)
        def inner(*args):
            if 'logged_in' not in session:
                flash("You must be logged in to see this page")
                return redirect('/')
            return f(*args)
        return inner
    return decorate


@app.route("/", methods=["GET", "POST"])
def index():
	return render_template("index.html")

@app.route("/register/<user_type>", methods=["GET", "POST"])
def register(user_type):
	base_url = "register_" + user_type + ".html"
	if request.method == "GET":
		return render_template(base_url)
	else:
                account = register_user(user_type, request.form, db)
		if request.form['b'] == "Submit":
			if request.form['confirm_password'] == request.form['password']:
				create_account(user_type, account, db)
				flash(user_type + ": You have succesfully created an account")
				return render_template("base.html")
			else:
				flash("Passwords do not match")
				return render_template(base_url)

@app.route("/login", methods=["GET", "POST"])

# authenticates user, logs him into session. there are two different login pages:
# login/tutee and login/tutor
@app.route("/login/<user_type>", methods=["GET", "POST"])
def login(user_type):
    if request.method == "GET":
        return render_template("login.html")
    else:
        email = request.form["email"]
        password = request.form["password"]
        if request.form['b'] == "Submit":
            user = authenticate(email, user_type, password, db)
            if user:
                # Loops over dictionary, creates new session element for each key
                for key in user.keys():
                    session[key] = user[key]
                session["logged_in"] = True
                flash("Welcome, " + session['first_name'])
                return redirect("homepage")
            else:
                flash("Your username or password is incorrect")
                return render_template("login.html")

@app.route("/homepage", methods=["GET", "POST"])
@auth("/homepage")
def homepage():
    if request.method == "GET":
        return render_template("homepage.html")
    else:
        if request.form['b']=="Log Out":
            return logout()

@app.route("/search", methods=["GET", "POST"])
def search():
        if request.method == "GET":
                return render_template("search.html") 
        else:
                if request.form['b'] == "Submit":
                        tutor_list = search_operation(request.form, db, session)
                        flash(tutor_list)
                        return render_template("base.html") #Will redirect to a search return page, temp for testing purposes of returns

def logout():
    session.pop('logged_in', None)
    flash("You have been logged out")
    return redirect('/')

if __name__ == "__main__":
	app.debug = True
	app.secret_key = "shhhhhh"
	app.run()
