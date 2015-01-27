import random
from googlemaps import locate
from utils import update_tutor, find_tutor, calculate_distance

#Returns list of possible tutors, based on course requested and the possible times given. times is a list of strings, each string is formatted day;hours;addresses.
#Concept: First seperates out all tutors free on specified days and with specified subjects. Then begins operating on point system: Points accorded, (listed from most valuable to least): hours matching, address proximity, courses matching, school matching, grade matching
def search_operation(form, db, session):
        subject = form["subject"]
        day = form["0-day"]

        print form
        print session

        tutor_list = db.tutors.find({"%s"%subject:True, day:True})

        tutor_ret = [] # list of tutors to be returned

        

        #for each tutor on the new list, give them a score based on secondary features
        for tutor in tutor_list:
                match_score = 0.0
                email = tutor['email']
                addresses = []
                #find the days for which addresses work
                try:
                        tutee_home_school = form.getlist("0-address")
                        #tutor_home_school = tutor['days'][day]['addresses']
                       
                        tutee_address = session["Home_Address"]
                        tutor_address = tutor["Home_Address"]
                        
                        
                        # tutor_address = tutor[tutor_home_school]
                        
                        #tutor_address = tutor["%s_Address" % tutor_home_school] #get the dictionary of the actual address info

                        #tutee_home_school = form["%s_Address" % day] #is the tutee home or school for that day
                        #tutee_address = session["%s_Address" % tutee_home_school] # get the dictionary of tutee's actual address info that day

                        if (tutor_address["zipcode"] == tutee_address["zipcode"]):
                                match_score += 4.0
                                distance = calculate_distance(tutor_address, tutee_address)
                                match_score += float(3 - distance)

                                #timing calculations
                                
                        tutee_start = float(form["0-start_hour"]) + (float(form["0-start_minute"]) * .01)
                        if form["0-start_type"] == "PM":
                                tutee_start += 12

                                

                        tutee_end = float(form["0-end_hour"]) + (float(form["0-end_minute"]) * .01)
                        if form["0-end_type"] == "PM":
                                tutee_end += 12
                                       
                               
                        best_time = -99999
                        for d in tutor['days'][day]:
                                
                                tutor_start = float(d["start_hour"]) + (float(d["start_min"]) *.01)
                                if d["start_type"] == "PM":
                                        tutor_start += 12
                                
                                tutor_end = float(d["end_hour"]) + (float(d["end_min"]) *.01)
                                if d["end_type"] == "PM":
                                        tutor_end += 12 

                                score = 0.0;
                                if (tutee_end > tutor_start):
                                        score += float(tutee_end - tutor_start) * 5
                                if (tutee_end > tutor_end):
                                        score -= float(tutee_end - tutor_end) * 5
                                if (tutee_start > tutor_start):
                                        score -= float(tutee_start - tutor_start) * 5
                                if (score > best_time):
                                        best_time = score
                        match_score += best_time
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
