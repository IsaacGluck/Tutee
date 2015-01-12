from flask import Flask, render_template, request, flash, session
from pymongo import Connection
from search import search_operation
from utils import authenticate, create_account, register_user
import hashlib, uuid
import random


app = Flask(__name__)

## mongo 
conn = Connection()
db = conn['users']

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
def login():
	if request.method == "GET":
		return render_template("login.html")
	else:
		email = request.form["email"]
		password = request.form["password"]
		user_type = request.form["user_type"]
	if request.form['b'] == "Submit":
		if authenticate(email, user_type, password, db):
			flash("You have succesfully logged in")
			session['email'] = email
			return render_template("base.html")
		else:
			flash("Your username or password is incorrect")
			return render_template("login.html")


@app.route("/search", methods=["GET", "POST"])
def search():
        if request.method == "GET":
                return render_template("search.html") 
        else:
                if request.form['b'] == "Submit":
                        tutor_list = search_operation(request.form, db, session)
                        flash(tutor_list)
                        return render_template("base.html") #Will redirect to a search return page, temp for testing purposes of returns

if __name__ == "__main__":
	app.debug = True
	app.secret_key = "shhhhhh"
	app.run()
