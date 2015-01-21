import hashlib, uuid
import math
import datetime
from time import ctime
from googlemaps import locate

#misc useful helper functions

# matches login attempts with user, returns user's account dictionary
def authenticate(email, user_type, confirm_password, db):
        if user_type == "tutee": 
		user = db.tutees.find_one( { 'email' : email } , { "_id" : False } )
	else:   
		user = db.tutors.find_one( { 'email' : email } , { "_id" : False }  )
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

# update_dict must be in the form {field_to_update : new_val}
def update_tutor(email, update_dict, db):
        db.tutors.update({'email' : email}, {'$set' : update_dict}, upsert=False)
        return True

def update_tutee(email, update_dict, db):
        db.tutees.update({'email' : email}, {'$set' : update_dict}, upsert=False)
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

        password = form["password"]
        salt = uuid.uuid4().hex #creates salt, a randomized string attached to end of password before hashing to prevent password compromisation even if hacker knew the hashing algo
        hash_pass = hashlib.sha512(salt + password).hexdigest() #prepend the salt to the password, hash using sha512 algorithm, use hexdigest to store as string
        account['salt'] = salt
        account['password'] = hash_pass
        account['school'] = form["school"]
        account['grade'] = form["grade"]
        account['conversations'] = {}
        
        a1 = form["address1"]
        a1_type = form["address1_hs"] #is this address for home or for school
        loc = locate(a1) #returns three part array, longtitude, latitude, and zip, for parameter address

        address1 = {}
        address1["longitude"] = loc[0] #longitude
        address1["latitude"] = loc[1] #latitude
        address1["zipcode"] = loc[2] #zipcode
        address1["address"] = a1 #actual address
        account["%s_Address" % a1_type] = address1 #store dictionary of all a1's info

        if user_type == "tutor":
                account['courses'] = form["courses"]
                #for each subject a tutor lists, it will have a seperate element in the dictionary with value "True"
                subject = form['subjects']
                account['%s' % subject] = True
                times = form["times"]
                td = times.split(";")
                x = 0
                #each day is given seperate element with value being a dictionary of time, address
                while x < len(td):
                        account['%s' % td[x]] = {"time": td[x+1], "address": form['Day1_Address']}
                        x += 2
                account['match_score'] = 0.0 #used in comparing for searches
        return account


#sends message by updating the "conversations" key for each user. Conversations' value is a dictionary, each key being the username of the other side of a given conversation. The value of each such key is a list of dictionaries, each dictionary containing a given message's content, sender, and time of sending. Example:
# 'conversations': {person_talked_to: [{'sender':person_talked_to/me, 'message_text':'sup', 'time':'12:04:50', 'date':Jan-20-2015}, more messages....], more people....}
def send_message(form, session, db):
        recipient_username = form['recipient']
        message = form['message']
        sender_user_type = session['type']
        if sender_user_type == "Tutor":
                recipient_cursor = db.tutees.find({'username':recipient_username})
        else:
                recipient_cursor = db.tutors.find({'username':recipient_username})
        for t in recipient_cursor:
                recipient = t
        conversations = recipient['conversations'] #list of dictionaries, each dictionary being a message that this recipient has already recieved
        time_total = str(ctime())
        date = time_total[4:10] + ", " + time_total[20:25]
        time = time_total[11:19]

        #first update the dictionary of the recipient of the message
        new_message = {'sender':session['username'], 'message_text':message, 'time':time, 'date':date}
        #check if this conversation already exists. If so incorporate rest of conversation
        if conversations.has_key(session['username']): #if they've already talked
                add_message = conversations[session['username']]
                add_message.append(new_message) #update the existant message chain,
                conversations[session['username']] = add_message #insert as the new value in dict
        else:
                conversations[session['username']] = [new_message]
        if sender_user_type == "Tutor":
                update_tutee(recipient['email'], {'conversations':conversations}, db)
        else:
                update_tutor(recipient['email'], {'conversations':conversations}, db)
        
        #update dictionary of the sender
        conversations = session['conversations'] #list of dictionaries, each dictionary being a message that this recipient has already recieved
        new_message = {'sender':session['username'], 'message_text':message, 'time':time, 'date':date}
        if conversations.has_key(recipient['username']):
                add_message = conversations[recipient['username']]
                add_message.append(new_message)
                conversations[recipient['username']] = add_message
        else:
                conversations[recipient['username']] = [new_message]
        if sender_user_type == "Tutor":
                update_tutor(session['email'], {'conversations':conversations}, db)
        else:
                update_tutee(session['email'], {'conversations':conversations}, db)
        return message + " sent on " + date + " by " + session['username']


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
