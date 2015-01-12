import hashlib, uuid
from googlemaps import locate

#misc useful helper functions

# matches login attempts with user
def authenticate(email, user_type, confirm_password, db):
	if user_type == "tutee": 
		user = db.tutees.find_one( { 'email' : email } )
	else:   
		user = db.tutors.find_one( { 'email' : email } )
	if user == None:
		return False
	salt = user["salt"]
	hash_pass = user["password"]
	hash_confirm = hashlib.sha512(salt + confirm_password).hexdigest()
	if hash_pass == hash_confirm:
		return True
	else:
		return False

#helper method to find a tutor given an email
def find_tutor(email, db):
    user = db.tutors.find_one({'email':email})
    return user

# update_dict must be in the form {field_to_update : new_val}
def update_tutor(email, update_dict, db):
        db.tutors.update({'email' : email}, {'$set' : update_dict}, upsert=False)
        return True


def create_account(user_type, account, db):
	if user_type == "tutor":
		return db.tutors.insert(account)
	return db.tutees.insert(account)

def register_user(user_type, form, db):
        account = {}
        account['match_score'] = 0
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
        print "add " + str(a1)
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
        #print account
        return account
