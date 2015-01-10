from flask import Flask, render_template, request, flash
from pymongo import Connection
import hashlib, uuid
import random

app = Flask(__name__)

## Mongo ##
conn = Connection()
db = conn['users']


names = ['thluffy','dennis','bucky','doughjoe',
         'victor','jesus', 'coby', 'isaac', 'aida', 'leslie', 'z', 'cat', 'lou', 'jake', 'fred', 'bob', 'lee', 'rob', 'ulyses', 'jackson', 'stone']
school = ['Stuyvesant', 'Bard', 'Bronx Science']
grade = [9, 10, 11, 12]
subs = ['Chemistry', 'English', 'Physics', 'Biology']
dates = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']

dlist = []
for i in range(20):
        d = {'first_name':random.choice(names),
             'school':random.choice(school),
             'grade':random.choice(grade),
             'subjects':[random.choice(subs), random.choice(subs)],
             'days':[random.choice(dates), random.choice(dates)],
             
        }
        dlist.append(d)

db.tutors.insert(dlist)

tut = {
        'first_name':random.choice(names),
        'school':random.choice(school),
        'grade':random.choice(grade),
        'subjects':['English', 'Physics'],
        'days':['Mon', 'Wed'],
        'address':'925 West End Ave',
}



@app.route("/", methods=["GET", "POST"])
def index():
	return render_template("index.html")

def register_user(user_type, form):
        account = {}
        account['first_name'] = form["first_name"]
        account['last_name'] = form["last_name"]
        account['type'] = user_type
        account['email'] = form["email"]

        password = form["password"]
        salt = uuid.uuid4().hex #creates salt, a randomized string attached to end of password before hashing to prevent password compromisation even if hacker knew the hashing algo
        hash_pass = hashlib.sha512(salt + password).hexdigest() #prepend the salt to the password, hash using sha512 algorithm, use hexdigest to store as string
        account['salt'] = salt
        account['password'] = hash_pass
        account['school'] = form["school"]
        account['grade'] = form["grade"]
        if user_type == "tutor":
                account['courses'] = form["courses"]
                account['subjects'] = form["subjects"]
                account['times'] = form["times"]
                account['match_score'] = 0
        return account

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
        #First make list of days tutee is available
        days = []
        for time in times:
                t = time.split(";")
                days.append(t[0])
        #create list tutors filled with all tutors with right subject and free day(s)

        print subject

        for day in days:
                tutor_list = db.tutors.find({"subjects.first":subject})
        
        print("COUNTTTTTTTTT: " + str(tutor_list.count()))
                
        #for each tutor on the new list, give them a score based on secondary features
        for tutor in tutor_list:
                print tutor
                score = 0
                #print(tutor['school'])
                #if tutor['school'] == tut['school']:
                 #       score += 1
                # it's a bit better if they go to the same school
                #score += (tutor['grade'] - tut['grade'])/5
                #An older tutor is preferable

                

@app.route("/register/<user_type>", methods=["GET", "POST"])
def register(user_type):
	base_url = "register_" + user_type + ".html"
	if request.method == "GET":
		return render_template(base_url)
	else:
                account = register_user(user_type, request.form)
		if request.form['b'] == "Submit":
			if authenticate(account, request.form['confirm_password']):
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
                                new_req += ";" + tut['address'] #to be replaced with sessions use to find the current user's home/ school address
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
