import random
from googlemaps import locate
from utils import update_tutor, find_tutor, calculate_distance

#Returns list of possible tutors, based on course requested and the possible times given. times is a list of strings, each string is formatted day;hours;addresses.
#Concept: First seperates out all tutors free on specified days and with specified subjects. Then begins operating on point system: Points accorded, (listed from most valuable to least): hours matching, address proximity, courses matching, school matching, grade matching
def search_operation(form, db, session):
        courses = form["courses"]
        subject = form["subjects"]
        days = form.getlist("days")


        #create list tutor_list filled with all tutors with right subject and free day(s)
        for day in days:
                tutor_list = db.tutors.find({"%s"%subject:True, "%s"%day:{ '$exists': True }})
                
        #print("COUNTTTTTTTTT: " + str(tutor_list.count()))
        
        tutor_ret = [] # list of tutors to be returned

        #for each tutor on the new list, give them a score based on secondary features
        for tutor in tutor_list:
                match_score = 0.0
                email = tutor['email']
                addresses = []
                #find the days for which addresses work
                for day in days:
                        try:
                                tutor_home_school = tutor[day]["address"] # if tutor has an element for that day, find whether it's home or school (that is what they store)
                                tutor_address = tutor["%s_Address" % tutor_home_school] #get the dictionary of the actual address info

                                tutee_home_school = form["%s_Address" % day] #is the tutee home or school for that day
                                tutee_address = session["%s_Address" % tutee_home_school] # get the dictionary of tutee's actual address info that day
                                if (tutor_address["zipcode"] == tutee_address["zipcode"]):
                                        match_score += 4.0
                                distance = calculate_distance(tutor_address, tutee_address)
                                match_score += float(3 - distance)

                                #timing calculations
                                
                                tutee_start = form["%s_Time_Start" % day]
                                tutee_end = form["%s_Time_End" % day]
                                
                                best_time = -99999;
                                for d in tutor[day]:
                                
                                        tutor_start = d["time_start"]
                                        tutor_end = tutor[day]["time_end"]
                                        #if the tutor starts
                                        if (tutee_end > tutor_start):
                                        match_score += float(tutee_end - tutor_start) * 5
                                        if (tutee_end > tutor_end):
                                                match_score -= float(tutee_end - tutor_end) * 5
                                                if (tutee_start > tutor_start):
                                                        match_score -= float(tutee_start - tutor_start) * 5
                        except:
                                pass
                
                if tutor['school'] == session['school']:
                        match_score += 1.0 # one point for going to the same school
                match_score += float(int(tutor['grade']) - int(session['grade']))/4 #An older tutor is preferable
                update_tutor(tutor['email'], {'match_score':match_score}, db)

        tutors = db.tutors.find({"match_score": {"$exists":True, "$nin":[0.0]}})
        tutors.sort("match_score")
        tutor_ret = []
        for t in tutors:
                tutor_ret.append(t)
                update_tutor(t['email'], {'match_score':0.0}, db) #clear the match scores of all
        return tutor_ret
