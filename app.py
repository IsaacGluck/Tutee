from flask import Flask, render_template, request, flash
from pymongo import Connection

app = Flask(__name__)

## Mongo ##
conn = Connection()
db = conn['users']

@app.route("/", methods=["GET", "POST"])
def index():
	return render_template("base.html")

def create_account(email, password, first_name, last_name):
	new_user = {
		'email': email,
		'password': password,
		'first_name': first_name,
		'last_name': last_name,
	}
	return db.accounts.insert(new_user)

@app.route("/register", methods=["GET", "POST"])
def register():
	if request.method == "GET":
		return render_template("register.html")
	else:
		first_name = request.form["first_name"]
		last_name = request.form["last_name"]
		email = request.form["email"]
		password = request.form["password"]
		confirm_password = request.form["confirm_password"]
		if request.form['b'] == "Submit":
			if password == confirm_password:
				create_account(email, password, first_name, last_name)
				flash("You have succesfully created an account")
				return render_template("base.html")
			else:
				flash("Passwords do not match")
				return render_template("register.html")

if __name__ == "__main__":
	app.debug = True
	app.secret_key = "shhhhhh"
	app.run()

