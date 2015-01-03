from flask import Flask, render_template, request, flash, session
from pymongo import Connection
import hashlib, uuid

app = Flask(__name__)

## mongo 
conn = Connection()
db = conn['users']

def create_account(user_type, account):
	if user_type == "tutor":
		return db.tutors.insert(account)
	return db.tutees.insert(account)

# matches login attempts with user
def authenticate(email, user_type, confirm_password):
	if user_type == "tutee": 
		user = db.tutees.find_one( { 'email' : email } )
	else:   
		user = db.tutors.find_one( { 'email' : email } )
	if user == None:
		return False
	salt = user["salt"]
	hash_pass = user["password"]
	hash_confirm = hashlib.sha512(salt + confirm_password).hexdigest()
	if hash_pass == hash_confirm:
		return True
	else:
		return False

@app.route("/", methods=["GET", "POST"])
def index():
	return render_template("index.html")

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

                password = request.form["password"]
                salt = uuid.uuid4().hex #creates salt, a randomized string attached to end of password before hashing to prevent password compromisation even if hacker knew the hashing algo
                hash_pass = hashlib.sha512(salt + password).hexdigest() #prepend the salt to the password, hash using sha512 algorithm, use hexdigest to store as string
                account['salt'] = salt
		account['password'] = hash_pass

		confirm_password = request.form["confirm_password"]
		account['school'] = request.form["school"]
		account['grade'] = request.form["grade"]
		if user_type == "tutor":
			account['courses'] = request.form["courses"]
			account['subjects'] = request.form["subjects"]
		if request.form['b'] == "Submit":
			if confirm_password == password:
				create_account(user_type, account)
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
		if authenticate(email, user_type, password):
			flash("You have succesfully logged in")
			session['email'] = email
			return render_template("base.html")
		else:
			flash("Your username or password is incorrect")
			return render_template("login.html")

if __name__ == "__main__":
	app.debug = True
	app.secret_key = "shhhhhh"
	app.run()

