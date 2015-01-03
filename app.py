from flask import Flask, render_template, request, flash
from pymongo import Connection

app = Flask(__name__)

## Mongo ##
conn = Connection()
db = conn['users']

@app.route("/", methods=["GET", "POST"])
def index():
	return render_template("base.html")

def create_account(user_type, account):
	if user_type == "tutor":
		return db.tutors.insert(account)
	return db.tutees.insert(account)

@app.route("/register/<user_type>", methods=["GET", "POST"])
def register(user_type):
	base_url = "register_" + user_type + ".html"
	if request.method == "GET":
		return render_template(base_url)
	else:
		account = {}
		account['first_name'] = request.form["first_name"]
		account['last_name'] = request.form["last_name"]
		account['email'] = request.form["email"]
		account['password'] = request.form["password"]
		confirm_password = request.form["confirm_password"]
		account['school'] = request.form["school"]
		account['grade'] = request.form["grade"]
		if user_type == "tutor":
			account['courses'] = request.form["courses"]
			account['subjects'] = request.form["subjects"]
		if request.form['b'] == "Submit":
			if account['password'] == confirm_password:
				create_account(user_type, account)
				flash(user_type + ": You have succesfully created an account")
				return render_template("base.html")
			else:
				flash("Passwords do not match")
				return render_template(base_url)

if __name__ == "__main__":
	app.debug = True
	app.secret_key = "shhhhhh"
	app.run()

