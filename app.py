from flask import Flask, render_template, request, flash
from pymongo import Connection
from googlemaps import locate
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
subs = ['chemistry', 'English', 'Physics', 'Biology']
dates = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']

dlist = []
for i in range(30):
        d = {'first_name':random.choice(names),
             'school':random.choice(school),
             'grade':random.choice(grade),
             '%s'%random.choice(subs):True,
             '%s'%random.choice(dates):'1-8',
             '%s'%random.choice(dates):'1-8',
        }
        dlist.append(d)

#db.tutors.insert(dlist)

#db.tutors.remove({})



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
        
        a1 = form["address1"]
        a1_type = form["address1_hs"] #is this address for home or for school
        loc = locate(a1) #returns three part array, longtitude, latitude, and zip, for parameter address

        address1 = {}
        address1["longitude"] = loc[0] #longitude
        address1["latitude"] = loc[1] #latitude
        address1["zipcode"] = loc[2] #zipcode
        address1["address"] = a1 #actual address
        account["%s_address" % a1_type] = address1 #store dictionary of all a1's info

        if user_type == "tutor":
                account['courses'] = form["courses"]
                #for each subject a tutor lists, it will have a seperate element in the dictionary with value "True"
                for subject in form['subjects']:
                        account['%s' % subject] = True
                times = form["times"]
                td = times.split(";")
                x = 0
                #each day is given seperate element with value being a dictionary of time, address
                while x < len(td):
                        account['%s' % td[x]] = {"time": td[x+1], "address": td[x+2]}
                        x += 3
                account['match_score'] = 0 #used in comparing for searches
        print account
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
        courses = form["courses"]
        subjects = form["subjects"]
        days = form.getlist("days")
        times = []
        for d in days:
                hour = request.form["%s" % d + "_Time"]
                new_req = d + ";" + hour
                #addresses = request.form.getlist("%s" % d + "_Address")
                # for a in addresses:
                #     new_req += ";" + tut['address'] #to be replaced with sessions use to find the current user's home/ school address
                #other_add = request.form["%s" % d + "_Other"]
                #if other_add:
                #       new_req += ";" + other_add
                times.append(new_req)

        #First make list of days tutee is available
        ds = []
        for time in times:
                t = time.split(";")
                ds.append(t[0])
                

        #create list tutor_list filled with all tutors with right subject and free day(s)
        for day in ds:
                tutor_list = db.tutors.find({"%s"%subject:True, "%s"%day:{ '$exists': True }})
                        
        #print("COUNTTTTTTTTT: " + str(tutor_list.count()))
        
        #for each tutor on the new list, give them a score based on secondary features
        for tutor in tutor_list:
                match_score = 0
                addresses = []
                #find the days for which addresses work
                for day in ds:
                        try:
                                tutor_home_school = tutor[day]["address"] # if tutor has an element for that day, find whether it's home or school (that is what they store)
                                tutor_address = tutor["%s_address" % tutor_home_school] #get the dictionary of the actual address info

                                tutee_home_school = form["%s_Address" % day] #is the tutee home or school for that day
                                tutee_address = tut["%s_address" % tutee_home_school] # get the dictionary of tutee's actual address info that day
                                if (tutor_address["zipcode"] == tutee_address["zipcode"]):
                                        match_score += 4
                        except: #that means tutor doesn't have an element for that day
                                pass
                
                if tutor['school'] == tut['school']:
                        match_score += 1 # one point for going to the same school
                score += (tutor['grade'] - tut['grade'])/5 #An older tutor is preferable

                

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
                if request.form['b'] == "Submit":
                        tutor_list = search_operation(request.form)
                        flash(tutor_list)
                        return render_template("base.html") #Will redirect to a search return page, temp for testing purposes of returns
                        

if __name__ == "__main__":
	app.debug = True
	app.secret_key = "shhhhhh"
	app.run()
