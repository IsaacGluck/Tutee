from flask import Flask, render_template, request, flash, session, redirect, url_for
from pymongo import Connection
import gridfs
from search import search_operation
from utils import authenticate, create_account, register_user, send_message, update_tutor, update_tutee, find_tutor, find_user, user_exists, create_days

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
        def inner(*args, **kwargs):
            if 'logged_in' not in session:
                flash("You must be logged in to see this page")
                return redirect('/')
            return f(*args, **kwargs)
        return inner
    return decorate

def check_tut(page):
    def decorate(f):
        @wraps(f)
        def inner(*args, **kwargs):
            if 'type' in session:
                if session['type'] == "tutor":
                    flash("You must be a tutee to see this page")
                    return redirect('/homepage')
            return f(*args, **kwargs)
        return inner
    return decorate
                

## FOR TESTING
@app.route("/register_test", methods=["GET", "POST"])
def register_test():
    if request.method == "GET":
       return render_template("register_update.html")

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
        return redirect(url_for('login'))
    else:
        return render_template(base_url, form=form, user_type=user_type)

# authenticates user, logs him into session. there are two different login pages:
# login/tutee and login/tutor
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form["username"]
        password = request.form["password"]
        if request.form['b']:
            if request.form['b'] == "login_tutee":
                user_type = "tutee"
            else:
                user_type = "tutor"
            #print(request.form)
            #print(user_type)
            user = authenticate(username, user_type, password, db)
            #print(user)
            if user:
                #print("UR A USER")
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
    user = find_user(session["username"], db)
    appts = user["appts"]
    print(appts)
    if request.method == "GET":
        return render_template("homepage.html", appts=appts)
    else:
        print(request.form)
        if request.form['b'] == 'Complete':
            appt = appts.pop(int(request.form['index']))
            flash("You have completed an appointment!")
            db.tutees.update( {'username' : appt['tutee'] }, { '$set' : {'appts' : appts} })
            db.tutors.update( {'username' : appt['tutor'] }, { '$set' : {'appts' : appts} })
            return render_template("homepage.html", appts=appts)
        if request.form['s']:
            if request.form['s'] == "Log Out":
                return logout()



@app.route("/profile/<username>", methods=["GET","POST"])
@auth("/profile/<username>")
def profile(username):
    if request.method == "GET":
        user = find_user(username, db)
        flasher = {}
        for key in user:
            flasher[key] = str(user[key])
        flash(flasher)
        #print 'username' + user['username']
        return render_template("profile.html")
    if request.method == "POST":
        if request.form['s'] == "Log Out":
            return logout()
        if request.form['s'] == "Make Appointment":
            message = send_message(request.form, session, db)
            flash(message)
            return redirect("inbox")


@app.route("/search", methods=["GET", "POST"])
@auth("/search")
@check_tut("/search")
def search():
        if request.method == "GET":
            return render_template("search.html") 
        else:
            print request.form
            if request.form['s'] == "Log Out":
                return logout() 
            if request.form['s'] == "Submit":
                tutor_list = search_operation(request.form, db, session)
                return render_template("search_results.html", tutor_list=tutor_list)
            if request.form['s'] == "Make Appointment":
                print(request.form)
                tutor_username = request.form['username']
                ## create_appointment    (tutor,          tutee,               subject,                 course)
                appt = create_appointment(tutor_username, session['username'], request.form["subject"], request.form["class"], request.form)
                ## print(appt)
                db.tutees.update( {'username' : session['username'] }, { '$addToSet' : {'appts' : appt} })
                db.tutors.update( {'username' : tutor_username      }, { '$addToSet' : {'appts' : appt} })
                flash("You have succesfully added your appt!")
                return redirect(url_for("homepage"))


@app.route("/settings/<settings_type>", methods=["GET","POST"])
@auth("/settings/<settings_type>")
def update_settings(settings_type):
    if request.method == "GET":
        html_file = "settings_" + settings_type + ".html"
        days = [];
        if session["type"] == "tutor":
            for k in session['days'].keys():
                for x in session['days'][k]:
                    days.append(x);
                
        print days
        session['jdays']=json.dumps(days)
        return render_template(html_file,days=json.loads(session['jdays']),dicts=days)
    if request.method == "POST":
        if request.form["s"] == "Log Out":
            return logout()
        if request.form["s"] == "Update Profile":
            new_account = {}
            old_email = session["email"]
            for key in request.form.keys():
                new_account[key] = request.form[key]
                session[key] = request.form[key]
            if session["type"] == "tutor":
                update_tutor(old_email, new_account, db)
            elif session["type"] == "tutee":
                update_tutee(old_email, new_account, db)
            flash("You have succesfully updated your settings")
            return redirect(url_for("homepage"))
        if request.form["s"] == "Update Times":
            print request.form
            days = create_days(request.form)
            new_account = {}
            new_account['days'] = days
            print days
            update_tutor(session["email"], new_account, db)
            session['days'] = days
            return redirect(url_for("update_settings", settings_type="times"))
        if request.form["s"] == "Update Profile Picture":
            # data = request.form["pic"]
            # file_id = fs.put(open(str(data), "rb").read()) 
            # update_dict = {"pic_id":file_id}
            # if session["type"]=="tutee":
            #     update_tutee(session["email"], update_dict, db)
            # else:
            #     update_tutor(session["email"], update_dict, db)
            return redirect("homepage")
                
@app.route("/inbox", methods=["GET","POST"])
@auth("/inbox")
def inbox():
    if request.method == "GET":
        if session['type'] == "tutor":
            update_tutor(session['email'], {'count_unread':0}, db)
        else:
            update_tutee(session['email'], {'count_unread':0}, db)
        session['count_unread'] = 0
        return render_template("inbox.html")
    if request.method == "POST":
        print request.form
        if request.form['s'] == "Log Out":
            return logout()
        if request.form['s'] == "Send Message":
            message = send_message(request.form, session, db)
            flash(message)
            return redirect("inbox")
        if request.form['s'] == "Reply":
            print request.form
            message = send_message(request.form, session, db)
            flash(message)
            return redirect("inbox")


def logout():
    session.pop('logged_in', None)
    flash("You have been logged out")
    return redirect('/')

def create_appointment(tutor, tutee, subject, course,form):
    appt = {}
    appt['tutor'] = tutor
    appt['tutee'] = tutee
    appt['subject'] = subject
    appt['class'] = course
    appt['day'] = form['0-day']
    appt['start_time'] = form['0-start_hour'] + ":" + form['0-start_minute'] + form['0-start_type']
    appt['end_time'] = form['0-end_hour'] + ":" + form['0-end_minute'] + form['0-end_type']
    appt['location'] = form['0-address']
    
    return appt

if __name__ == "__main__":
	app.debug = True
	app.secret_key = "shhhhhh"
	app.run()
