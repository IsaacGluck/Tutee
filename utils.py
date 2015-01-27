import hashlib, uuid
import math
import datetime
from time import ctime
from googlemaps import locate

#misc useful helper functions

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

# matches login attempts with user, returns user's account dictionary
def user_exists(email, user_type, db):
    check = None
    if user_type == "tutee":
        check = db.tutees.find_one({'email':email})
    else:
        check == db.tutor.find_one({'email':email})
    if check:
        return True
    return False

def authenticate(username, user_type, confirm_password, db):
    if user_type == "tutee":
        user = db.tutees.find_one( { 'username' : username } , { "_id" : False } )
    else:   
        user = db.tutors.find_one( { 'username' : username } , { "_id" : False }  )
    if user == None:
        return None
    salt = user["salt"]
    hash_pass = user["password"]
    hash_confirm = hashlib.sha512(salt + confirm_password).hexdigest()
    if hash_pass == hash_confirm:
        return user
    else:
        
        return None

#helper method to find a tutor given an email
def find_tutor(email, db):
        user = db.tutors.find_one({'email':email})
        return user

#if you don't know the user type
def find_user(username, db):
        user = db.tutors.find_one({'username':username})
        if user == None:
                user = db.tutees.find_one({'username':username})
        return user

# update_dict must be in the form {field_to_update : new_val}
def update_tutor(email, update_dict, db):
        db.tutors.update({'email' : email}, {'$set' : update_dict}, upsert=True)
        return True

def update_tutee(email, update_dict, db):
    db.tutees.update({'email' : email}, { '$set' : update_dict }, upsert=True)
    return True

def create_account(user_type, account, db):
	if user_type == "tutor":
		return db.tutors.insert(account)
	return db.tutees.insert(account)

def register_user(user_type, form, db):
        account = {}
        account['first_name'] = form["first_name"]
        account['last_name'] = form["last_name"]
        account['type'] = user_type
        account['username'] = form["username"]
        account['email'] = form["email"]
        account['appts'] = []
        password = form["password"]
        salt = uuid.uuid4().hex #creates salt, a randomized string attached to end of password before hashing to prevent password compromisation even if hacker knew the hashing algo
        hash_pass = hashlib.sha512(salt + password).hexdigest() #prepend the salt to the password, hash using sha512 algorithm, use hexdigest to store as string
        account['salt'] = salt
        account['password'] = hash_pass
        account['school'] = form["school"]
        account['grade'] = form["grade"]
        account['conversations'] = {}
        account['count_unread'] = 0
        
        a1 = form["address1"]
        loc = locate(a1) #returns three part array, longtitude, latitude, and zip, for parameter address

        address1 = {}
        address1["longitude"] = loc[0] #longitude
        address1["latitude"] = loc[1] #latitude
        address1["zipcode"] = loc[2] #zipcode
        address1["address"] = a1 #actual address
        account["Home_Address"] = address1 #store dictionary of all a1's info

        a2 = form["address2"]
        loc2 = locate(a2) #returns three part array, longtitude, latitude, and zip, for parameter address

        address2 = {}
        address2["longitude"] = loc2[0] #longitude
        address2["latitude"] = loc2[1] #latitude
        address2["zipcode"] = loc2[2] #zipcode
        address2["address"] = a2 #actual address
        account["School_Address"] = address2 #store dictionary of all a1's info
   

        if user_type == "tutor":            
                
                # #print days
                # days  = create_days(form)
                # account['days'] = days
                # for k in days:
                #     print k
                #     account[k] = True
            
                courses = form.getlist('course')
                subjects = form.getlist('subject')
                account['courses'] = courses
                account['subjects'] = subjects
                
                for subject in subjects:
                    print subject
                    account[subject] = True
                    
                account['match_score'] = 0.0 #used in comparing for searches
                account['complete'] = 0
        # print account
        return account


#sends message by updating the "conversations" key for each user. Conversations' value is a dictionary, each key being the username of the other side of a given conversation. The value of each such key is a list of dictionaries, each dictionary containing a given message's content, sender, and time of sending. Example:
# 'conversations': {person_talked_to: [{'sender':person_talked_to/me, 'message_text':'sup', 'time':'12:04:50', 'date':Jan-20-2015}, more messages....], more people....}
def send_message(form, session, db):
        recipient_username = form['recipient']
        message = form['message']
        sender_user_type = session['type']
        if sender_user_type == "tutor":
                recipient_cursor = db.tutees.find({'username':recipient_username})
        else:
                recipient_cursor = db.tutors.find({'username':recipient_username})
        recipient = {}
        for t in recipient_cursor:
                recipient = t
        if recipient == {}:
                return "invalid recipient"
        conversations = recipient['conversations'] #list of dictionaries, each dictionary being a message that this recipient has already recieved
        time_total = str(ctime())
        date = time_total[4:10] + ", " + time_total[20:25]
        time = time_total[11:19]

        #first update the dictionary of the recipient of the message
        new_message = [{'sender':session['username'], 'message_text':message, 'time':time, 'date':date, 'unread':True}]
        #check if this conversation already exists. If so incorporate rest of conversation
        if conversations.has_key(session['username']): #if they've already talked
                add_message = conversations[session['username']]
                for x in add_message:
                        new_message.append(x) #so that new message is at the begginning
        conversations[session['username']] = new_message #insert as the new value in dict
        count = recipient['count_unread'] + 1 #increment user's count of unread messages
        if sender_user_type == "tutor":
                update_tutee(recipient['email'], {'conversations':conversations, 'count_unread':count}, db)
        else:
                update_tutor(recipient['email'], {'conversations':conversations, 'count_unread':count}, db)
        
        
        
        
        #update dictionary of the sender
        conversations = session['conversations'] #list of dictionaries, each dictionary being a message that this recipient has already recieved
        new_message = [{'sender':session['username'], 'message_text':message, 'time':time, 'date':date, 'unread':False}]
        if conversations.has_key(recipient['username']):
                add_message = conversations[recipient['username']]
                for x in add_message:
                        new_message.append(x)
        conversations[recipient['username']] = new_message
        if sender_user_type == "tutor":
                update_tutor(session['email'], {'conversations':conversations}, db)
        else:
                update_tutee(session['email'], {'conversations':conversations}, db)
        return message + " sent on " + date + " by " + session['username']


#takes dictionary of lists of messages, reorders each convo so most recent messages come first
def reverse(conversations):
        ret = {}
        for key in conversations.keys():
                conversations[key].reverse()
                ret[key] = conversations[key]
        return ret
        
                

#Calculates the distance given two dictionaries of addresses, using longitude and latitude
def calculate_distance(address1, address2):
        long1 = math.radians(address1["longitude"])
        lat1 = math.radians(address1["latitude"])
        long2 = math.radians(address2["longitude"])
        lat2 = math.radians(address2["latitude"])
        dlong = (long2 - long1) #distance between longs
        dlat = (lat2 - lat1) #distance between lats
        #these are computations found online for calculating distance
        a = math.pow((math.sin(dlat/2)),2) + math.cos(lat1) * math.cos(lat2) * math.pow((math.sin(dlong/2)),2)
        b = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        c = 3963.1 * b #multiply radius of the earth, 3963.1 miles
        return c

def create_days(form):
        days = {}
        num = int(form['counter']) + 1
        for i in range(num):
                day = {}
                dayName = form[str(i) + '-day']
                day['day'] = dayName
                day['addresses'] = form.getlist(str(i) + "-address")
                day['start_hour'] = form[str(i) + '-start_hour']
                day['start_min'] = form[str(i) + '-start_minute']
                day['start_type'] = form[str(i) + '-start_type']
                day['end_hour'] = form[str(i) + '-end_hour']
                day['end_min'] = form[str(i) + '-end_minute']
                day['end_type'] = form[str(i) + '-end_type']
                if days.has_key(dayName) == False:
                        days[dayName] = []
                days[dayName].append(day)
        return days

#quick helper to check if a picture has a legitimate file extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
