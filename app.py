from flask import Flask, render_template, request, flash, session, redirect, url_for
from pymongo import Connection
import gridfs
from search import search_operation
from utils import authenticate, create_account, register_user, send_message, update_tutor, update_tutee, find_tutor, find_user, user_exists 

import hashlib, uuid
import random
import json
from functools import wraps
from forms import RegisterForm

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
    form = RegisterForm()
    if form.validate_on_submit():
        if user_exists(request.form['email'], user_type, db):
            flash("A user with this email already exists")
            return render_template(base_url, form=form, user_type=user_type)
        account = register_user(user_type, request.form, db)
        create_account(user_type, account, db)
        flash(user_type + ": You have succesfully created an account")
        return redirect(url_for('login', user_type=user_type))
    else:
        flash("Email or password is not valid")
        return render_template(base_url, form=form, user_type=user_type)

# authenticates user, logs him into session. there are two different login pages:
# login/tutee and login/tutor
@app.route("/login/<user_type>", methods=["GET", "POST"])
def login(user_type):
    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form["username"]
        password = request.form["password"]
        if request.form['b'] == "Submit":
            user = authenticate(username, user_type, password, db)
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
        if request.form['s'] == "Send":
            message = send_message(request.form, session, db)
            flash(message)
            return redirect("homepage")
        if request.form['s'] == "Log Out":
            return logout()


@app.route("/profile/<username>", methods=["GET","POST"])
def profile(username):
    if request.method == "GET":
        user = find_user(username, db)
        flasher = {}
        for key in user:
            flasher[key] = str(user[key])
        flash(flasher)
        print 'username' + user['username']
        return render_template("profile.html")
    if request.method == "POST":
        if request.form['b'] == "Log Out":
            return logout()


@app.route("/search", methods=["GET", "POST"])
def search():
        if request.method == "GET":
                return render_template("search.html") 
        else:
                if request.form['b'] == "Submit":
                    tutor_list = search_operation(request.form, db, session)
                    return render_template("search_results.html", tutor_list=tutor_list)
                if request.form['b'] == "Make Appointment":
                    print(request.form)
                    tutor_username = request.form['username']
                    ## create_appointment    (tutor,          tutee,               subject,                 course)
                    appt = create_appointment(tutor_username, session['username'], request.form["subject"], request.form["class"])
                    print(appt)
                    db.tutees.update( {'username' : session['username'] }, { '$addToSet' : {'appts' : appt} })
                    db.tutors.update( {'username' : tutor_username      }, { '$addToSet' : {'appts' : appt} })
                    flash("You have succesfully added your appt!")
                    return redirect(url_for("homepage"))


@auth("/settings")
@auth("/settings/profile")
@app.route("/settings/<settings_type>", methods=["GET","POST"])
def update_settings(settings_type):
    if request.method == "GET":
        html_file = "settings_" + settings_type + ".html"
        return render_template(html_file)
    if request.method == "POST":
        if request.form["b"] == "Log Out":
            return logout()
        if request.form["b"] == "Update Profile":
            new_account = {}
            old_email = session["email"]
            for key in request.form.keys():
                new_account[key] = request.form[key]
                session[key] = request.form[key]
            if session["type"] == "tutor":
                update_tutor(old_email, new_account, db)
            elif session["type"] == "tutee":
                update_tutee(old_email, new_account, db)
            return redirect(url_for("homepage"))
        if request.form["b"] == "Update Profile Picture":
            # data = request.form["pic"]
            # file_id = fs.put(open(str(data), "rb").read()) 
            # update_dict = {"pic_id":file_id}
            # if session["type"]=="tutee":
            #     update_tutee(session["email"], update_dict, db)
            # else:
            #     update_tutor(session["email"], update_dict, db)
            return redirect("homepage")
                
@auth("/inbox")
@app.route("/inbox", methods=["GET","POST"])
def inbox():
    if request.method == "GET":
        return render_template("inbox.html")
    if request.method == "POST":
        if request.form['b'] == "Log Out":
            return logout()


def logout():
    session.pop('logged_in', None)
    flash("You have been logged out")
    return redirect('/')

def create_appointment(tutor, tutee, subject, course):
    appt = {}
    appt['tutor'] = tutor
    appt['tutee'] = tutee
    appt['subject'] = subject
    appt['class'] = course
    return appt

if __name__ == "__main__":
	app.debug = True
	app.secret_key = "shhhhhh"
	app.run()
