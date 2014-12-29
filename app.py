from flask import Flask, render_template, request, flash
##import mongo

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
	return render_template("base.html")
def create_account(email, password):
	return "Creating account"

@app.route("/register", methods=["GET", "POST"])
def register():
	if request.method == "GET":
		return render_template("register.html")
	else:
		email = request.form["email"]
		password = request.form["password"]
		confirm_password = request.form["confirm_password"]
		if request.form['b'] == "Submit":
			if password == confirm_password:
				return create_account(email, password)

			else:
				flash("Passwords do not match")
				return render_template("register.html")

if __name__ == "__main__":
	app.debug = True
	app.secret_key = "shhhhhh"
	app.run()

