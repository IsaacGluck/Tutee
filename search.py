import random
from googlemaps import locate
from utils import update_tutor, find_tutor

#################################################################################CODE FOR TESTING USE################################################################################################

names = ['thluffy','dennis','bucky','doughjoe',
         'victor','jesus', 'coby', 'isaac', 'aida', 'leslie', 'z', 'cat', 'lou', 'jake', 'fred', 'bob', 'lee', 'rob', 'ulyses', 'jackson', 'stone']
school = ['Stuyvesant', 'Bard', 'Bronx Science']
grade = [9, 10, 11, 12]
subs = ['chemistry', 'english', 'physics', 'biology']
dates = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
zips = [10025, 10026, 10027, 10028]
emails = ["coby.goldberg@gmail.com", "cob", "co", "ss", "a", "b", "c", "d", "e", "f","g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "zzzz", "z", "ghaga", "chake", "shake", "lake"]

dlist = []
x = 0
while x<30:
        d = {'first_name':random.choice(names),
             'school':random.choice(school),
             'grade':random.choice(grade),
             'email':emails[x],
             'chemistry':True,
             '%s'%random.choice(subs):True,
             '%s'%random.choice(dates):{"time:":'1-8', "address":"School"},
             '%s'%random.choice(dates):{"time:":'1-8', "address":"School"},
             "School_Address":{"longitude":80, "latitude":80, "zipcode":random.choice(zips), "address":"825 West End Avenue"},
        }
        dlist.append(d)
        x += 1

#db.tutors.insert(dlist)

#db.tutors.remove({})

#print db.tutors.find({'hello':{'$exists':True}})

tut = {
        'first_name':random.choice(names),
        'school':"Stuyvesant",
        'grade':9,
        'School_Address':{"longitude":80, "latitude":80, "zipcode":10026, "address":"825 West End Avenue"}
}

#####################################################################################################################################################################################################

#"tut" must be replaced by session (i.e. logged in person)

#Returns list of possible tutors, based on course requested and the possible times given. times is a list of strings, each string is formatted day;hours;addresses.
#Concept: First seperates out all tutors free on specified days and with specified subjects. Then begins operating on point system: Points accorded, (listed from most valuable to least): hours matching, address proximity, courses matching, school matching, grade matching
def search_operation(form, db, session):
        courses = form["courses"]
        subject = form["subjects"]
        days = form.getlist("days")
        times = []
        for d in days:
                hour = form["%s" % d + "_Time"]
                new_req = d + ";" + hour
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
        
        tutor_ret = [] # list of tutors to be returned

        #for each tutor on the new list, give them a score based on secondary features
        for tutor in tutor_list:
            match_score = 0
            email = tutor['email']
            addresses = []
            #find the days for which addresses work
            for day in ds:
                try:
                        tutor_home_school = tutor[day]["address"] # if tutor has an element for that day, find whether it's home or school (that is what they store)
                        tutor_address = tutor["%s_Address" % tutor_home_school] #get the dictionary of the actual address info

                        tutee_home_school = form["%s_Address" % day] #is the tutee home or school for that day
                        tutee_address = tut["%s_Address" % tutee_home_school] # get the dictionary of tutee's actual address info that day
                        if (tutor_address["zipcode"] == tutee_address["zipcode"]):
                                match_score += 4
                except:
                        pass
                        
            if tutor['school'] == tut['school']:
                    match_score += 1 # one point for going to the same school
                    print "+1"
            match_score += (tutor['grade'] - tut['grade'])/5 #An older tutor is preferable
            update_tutor(tutor['email'], {'match_score':match_score}, db)
            #print "score is: " + str(find_tutor(tutor['email'], db)['match_score'])

        tutors = db.tutors.find({"match_score": {"$exists":True}})
        tutors.sort("match_score")
        tutor_ret = []
        for t in tutors:
                tutor_ret.append(t)
        return tutor_ret
