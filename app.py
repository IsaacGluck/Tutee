from flask import Flask, render_template, request, flash
from pymongo import Connection
import hashlib, uuid

app = Flask(__name__)

## Mongo ##
conn = Connection()
db = conn['users']

@app.route("/", methods=["GET", "POST"])
def index():
	return render_template("index.html")

def create_account(user_type, account):
	if user_type == "tutor":
		return db.tutors.insert(account)
	return db.tutees.insert(account)

#matches login attempts with user
def authenticate(account, confirm_password):
        salt = account['salt']
        hash_pass = account['password'] # the hashed version of the password (with salt)
        hash_confirm = hashlib.sha512(salt + confirm_password).hexdigest()
        if hash_pass == hash_confirm:
                return True
        else:
                return False

#Returns list of possible tutors, based on course requested and the possible times given. times is a list of strings, each string is formatted day;hours;addresses.
#Concept: First seperates out all tutors free on specified days and with specified subjects. Then begins operating on point system: Points accorded, (listed from most valuable to least): hours matching, address proximity, courses matching, school matching, grade matching
def search_operation(course, subject, times):
        tutors = []
        #First make list of days tutee is available
        days = []
        for time in times:
                t = time.split(";")
                days.append(t[0])
        #create list tutors filled with all tutors with right subject and free day(s)
        for day in days:
                tutors.append(list(db.tutors.find({"subjects":{"$in":[subject]}, "days":{"$in":[day]}}))))
        
        

@app.route("/register/<user_type>", methods=["GET", "POST"])
def register(user_type):
	base_url = "register_" + user_type + ".html"
	if request.method == "GET":
		return render_template(base_url)
	else:
		account = {}
		account['first_name'] = request.form["first_name"]
		account['last_name'] = request.form["last_name"]
                account['type'] = user_type
		account['email'] = request.form["email"]

                password = request.form["password"]
                salt = uuid.uuid4().hex #creates salt, a randomized string attached to end of password before hashing to prevent password compromisation even if hacker knew the hashing algo
                hash_pass = hashlib.sha512(salt + password).hexdigest() #prepend the salt to the password, hash using sha512 algorithm, use hexdigest to store as string
                account['salt'] = salt
		account['password'] = hash_pass

		confirm_password = request.form["confirm_password"]
		account['school'] = request.form["school"]
		account['grade'] = request.form["grade"]
                account['address1'] = request.form["address1"]
		if user_type == "tutor":
			account['courses'] = request.form["courses"]
			account['subjects'] = request.form["subjects"]
                        account['times'] = request.form["times"]
		if request.form['b'] == "Submit":
			if authenticate(account, confirm_password):
				create_account(user_type, account)
				flash(user_type + ": You have succesfully created an account")
				return render_template("base.html")
			else:
				flash("Passwords do not match")
				return render_template(base_url)

@app.route("/search", methods=["GET", "POST"])
def search():
        if request.method == "GET":
                return render_template("search.html") 
        else:
                courses = request.form["courses"]
                subjects = request.form["subjects"]
                days = request.form.getlist("days")
                times = []
                for d in days:
                        hour = request.form["%s" % d + "_Time"]
                        new_req = d + ";" + hour
                        addresses = request.form.getlist("%s" % d + "_Address")
                        for a in addresses:
                                new_req += ";" + account[a] #to be replaced with sessions use to find the current user's home/ school adress
                        other_add = request.form["%s" % d + "_Other"]
                        if other_add:
                                new_req += ";" + other_add
                        times.append(new_req)
                tutor_list = search_operation(courses, subjects, times)
                if request.form['b'] == "Submit":
                        flash(times)
                        return render_template("base.html") #Will redirect to a search return page, temp for testing purposes of returns
                        

if __name__ == "__main__":
	app.debug = True
	app.secret_key = "shhhhhh"
	app.run()
