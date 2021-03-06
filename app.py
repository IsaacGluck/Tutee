from flask import Flask, render_template, request, flash, session, redirect, url_for, send_from_directory
from pymongo import Connection
import gridfs
import os
from search import search_operation
from utils import authenticate, create_account, register_user, send_message, update_tutor, update_tutee, find_tutor, find_user, user_exists, create_days, allowed_file
from werkzeug import secure_filename
import tempfile
import hashlib, uuid
import random
import json
import urllib
from functools import wraps
from forms import RegisterForm
import shutil
from werkzeug.contrib.fixers import ProxyFix

app = Flask(__name__)

UPLOAD_FOLDER = tempfile.gettempdir() #for profile pictures
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY']="secret key"

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
    if request.method == "POST":
        print(request.form)
        user_type = request.form["type"]
        print(user_type)
        form = RegisterForm()
        print(form)
        if form.validate_on_submit():
            print("HELLO")
            if user_exists(request.form['email'], user_type, db):
                flash("A user with this email already exists")
                return render_template("register_update.html")
        account = register_user(user_type, request.form, db)
        create_account(user_type, account, db)
        return redirect(url_for('login'))
    else:
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
        if account == "IV":
            flash("Invalid address. Make sure it looks like: 825 West End Ave #4A, New York.")
            return redirect("register/%s"%user_type)
        create_account(user_type, account, db)
        return redirect(url_for('login'))
    if request.method=="POST":
        flash("Your email or password is not valid. Please try again.")
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
                return render_template("index.html")

@app.route("/homepage", methods=["GET", "POST"])
@auth("/homepage")
def homepage():
    user = find_user(session["username"], db)
    appts = user["appts"]
    print(appts)
    if request.method == "GET":
        return render_template("homepage.html", appts=appts)
    else:
        if 'b' in request.form:
            if request.form['b'] == 'Complete':
                appt = appts.pop(int(request.form['index']))
                flash("You have completed an appointment! Congrats")
                db.tutees.update( {'username' : appt['tutee'] }, { '$set' : {'appts' : appts} })
                db.tutors.update( {'username' : appt['tutor'] }, { '$set' : {'appts' : appts} })
                return render_template("homepage.html", appts=appts)
        if 's' in request.form:
            if request.form['s'] == "Log Out":
                return logout()
            if request.form['s'] == "Send":
                message = send_message(request.form, session, db)
                flash(message)
                return redirect("inbox")

@app.route("/profile/<username>", methods=["GET","POST"])
@auth("/profile/<username>")
def profile(username):
    if request.method == "GET":
        user = find_user(username, db)
        flasher = {}
        for key in user:
            ##print(user[key].encode())
            flasher[key] = str(user[key]).decode('utf-8')   
        flash(flasher)
        #print 'username' + user['username']
        return render_template("profile.html", courses=user["courses"], subjects=user["subjects"])
    if request.method == "POST":
        if request.form['s'] == "Log Out":
            return logout()
        if request.form['s'] == "Send Message":
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
                print request.form

                if request.form['0-day'] == "":
                    print "You must select a day"
                if len(request.form.getlist("0-address")) == 0:
                    print "You must select at least one location"
                if (request.form['0-start_hour'] == "") | (request.form['0-end_hour'] == ""):
                    print "You must select an hour for starting and ending times"
                if (request.form['0-start_minute'] == "") | (request.form['0-end_minute'] == ""):
                    print "You must select a minute for starting and ending times"
                if (request.form['0-start_type'] == "") | (request.form['0-end_type'] == ""):
                    print "You must select a type for starting and ending times"
                    
                tutor_list = search_operation(request.form, db, session)
                tutor_list.reverse() #to put highest score at top
                return render_template("search_results.html", tutor_list=tutor_list)
            if request.form['s'] == "Send Message":
                message = send_message(request.form, session, db)
                flash(message)
                return redirect("inbox")

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
        classes = [];
        subjects = [];
        print session
        if session["type"] == "tutor":
            for k in session['days'].keys():
                print k
                for x in session['days'][k]:
                    days.append(x);
            classes = session["courses"]
            subjects = session["subjects"]

        
                
        print days
        session['jdays']=json.dumps(days)
        session['jclasses'] = json.dumps(classes)
        session['jsubjects'] = json.dumps(subjects)
        return render_template(html_file,days=json.loads(session['jdays']),dicts=days,classes=json.loads(session['jclasses']), subjects=json.loads(session['jsubjects']))
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
            print days
            new_account = {}
            new_account['days'] = days
            new_account['complete'] = 1
            for k in days.keys():
                new_account[k] = True
            update_tutor(session["email"], new_account, db)
            session['days'] = days
            session['complete'] = 1

            return redirect(url_for("update_settings", settings_type="times"))

        if request.form["s"] == "Update Classes":
            courses = request.form.getlist("course")
            subs = request.form.getlist("subject")
            new_account = {}
            new_account['courses'] = courses
            new_account['subjects'] = subs
            for s in subs:
                new_account[s] = True
                session[s] = True
            session['courses'] = courses
            session['subjects'] = subs
            update_tutor(session['email'],new_account,db)
            return redirect(url_for("update_settings", settings_type="classes"))
                         
            
        if request.form["s"] == "Update Profile Picture":
            file = request.files['file']
            if file and allowed_file(file.filename): #check extension
                filename = secure_filename(file.filename)
                y = file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                url = url_for('uploaded_file', filename=filename)
                src = tempfile.gettempdir() + '/' + filename #tempfile.gettempdir() is flask's temporary storage directory

                img_storage = 'static/img/profile_pics/%s_%s' %(session['username'], filename)
                open(session["pic_id"][1:],"w").close() #close the current profile picture's file
                with open(img_storage, 'wb') as f:
                    shutil.copyfile(src, img_storage) #store the file in the Tutee system

                update_dict = {"pic_id":'../%s' % img_storage}
                if session["type"]=="tutee":
                    update_tutee(session["email"], update_dict, db)
                    u = find_user(session["username"], db)
                    session["pic_id"] = u["pic_id"]
                else:
                    update_tutor(session["email"], update_dict, db)
                    u = find_user(session["username"], db)
                    session["pic_id"] = u["pic_id"]
                return redirect("homepage")

            else: #invalid file name
                return redirect("settings/profile")


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
                
@app.route("/inbox", methods=["GET","POST"])
@auth("/inbox")
def inbox():
    if request.method == "GET":
        #automatically redirect to chat with most recent messenger, as fbook does
        username = ""
        for key in session["conversations"].keys():
            username = key
            break
        if username == "":
            flash("No messages yet, try starting a conversation.")
            return redirect('homepage')
        return redirect("inbox/%s"%username)


@app.route("/inbox/<username>", methods=["GET","POST"])
@auth("/inbox/<username>")
def conversation(username):
    if request.method == "GET":
        conversations = session['conversations']
        now_read = conversations[username]['unread_count'] #newly read messages
        
        conversations[username]['unread_count'] = 0 #this conversation now has all conversations read
        for message in conversations[username]['messages']:
            message['unread'] = False
        
        count_unread = session['count_unread'] - now_read

        if session['type'] == "tutor":
            update_tutor(session['email'], {'conversations':conversations, 'count_unread':count_unread}, db)
        else:
            update_tutee(session['email'], {'conversations':conversations, 'count_unread':count_unread}, db)
        session['count_unread'] = count_unread
        session['conversations'] = conversations

        convo = conversations[username]['messages']
        return render_template("inbox.html", username = username, convo = convo)
    if request.method == "POST":
        if request.form['s'] == "Log Out":
            return logout()
        if request.form['s'] == "Send Message":
            message = send_message(request.form, session, db)
            flash(message)
            return redirect("inbox/%s"%username)
        if request.form['s'] == "Reply":
            print request.form
            message = send_message(request.form, session, db)
            flash(message)
            return redirect("inbox/%s"%username)

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

app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == "__main__":
	app.debug = True
	app.secret_key = "shhhhhh"
	app.run()
