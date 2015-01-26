from flask import Flask, render_template, request, flash, session, redirect, url_for
from pymongo import Connection
import gridfs
from gridfs import GridFS
from search import search_operation
from utils import authenticate, create_account, register_user, send_message, update_tutor, update_tutee, find_tutor, create_days
import hashlib, uuid
import random
import json
from functools import wraps
app = Flask(__name__)

# mongo 
conn = Connection()
db = conn['users']

fs = gridfs.GridFS(db)

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
    if request.method == "GET":
	   return render_template("index.html")
    else:
        if request.form['b']=="Login":
            return redirect("/login/tutees")
        else:
            return redirect("/register/tutees")

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
        tutors = db.tutors.find()
        for t in tutors:
            print t['conversations']
        tutees = db.tutees.find()
        for t in tutees:
            print t['conversations']
        return render_template("homepage.html")
    else:
        if request.form['s'] == "Send":
            message = send_message(request.form, session, db)
            flash(message)
            return redirect("homepage")
        if request.form['b'] == "Log Out":
            return logout()

@app.route("/profile", methods=["GET","POST"])
@auth("/profile")
def profile():
    if request.method == "GET":
        return render_template("profile.html")

@app.route("/search", methods=["GET", "POST"])
def search():
        if request.method == "GET":
                return render_template("search.html") 
        else:
                if request.form['b'] == "Submit":
                        tutor_list = search_operation(request.form, db, session)
                        return render_template("search_results.html", tutor_list=tutor_list) #Will redirect to a search return page, temp for testing purposes of returns

@auth("/results")
@app.route("/results", methods=["GET", "POST"])
def results(tutor_list):
    if request.method == "GET":
        return render_template("search_results.html", tutor_list=tutor_list)


@auth("/settings")
@app.route("/settings/<settings_type>", methods=["GET","POST"])
def update_settings(settings_type):
    if request.method == "GET":
        html_file = "settings_" + settings_type + ".html"
        days = [];
        for k in session['days'].keys():
            for x in session['days'][k]:
                days.append(x);
                
        print days
        session['jdays']=json.dumps(days)
        return render_template(html_file,days=json.loads(session['jdays']),dicts=days)
    if request.method == "POST":
        if request.form["b"] == "Log Out":
            return logout()
        if settings_type == "profile":
            if request.form["b"] == "Update Profile":
                new_account = {}
                old_email = session["email"]
                for key in request.form.keys():
                    new_account[key] = request.form[key]
                    session[key] = request.form[key]
                update_tutor(old_email, new_account, db)
                return redirect("homepage")
            if request.form["b"] == "Update Profile Picture":
                data = request.form["pic"]
                gridin = fs.new_file()
                fileID = fs.put( fs.read(data)  )
                print(pic_id)
                update_dict = {"pic_id":pic_id}
                if session["type"]=="tutee":
                    update_tutee(session["email"], update_dict, db)
                else:
                    update_tutor(session["email"], update_dict, db)
                return render_template()
        if request.form["b"] == "Update Times":
            print request.form
            days = create_days(request.form)
            new_account = {}
            new_account['days'] = days
            print days
            update_tutor(session["email"], new_account, db)
            session['days'] = days
            return redirect(url_for("update_settings", settings_type="times"))
            #return render_template("settings_times.html",days=json.loads(session['jdays']))           

def logout():
    session.pop('logged_in', None)
    flash("You have been logged out")
    return redirect('/')

if __name__ == "__main__":
	app.debug = True
	app.secret_key = "shhhhhh"
	app.run()
