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

        tutor_list = db.tutors.find({"%s"%subject:True, "%s"%day:True})

        tutor_ret = [] # list of tutors to be returned

        #for each tutor on the new list, give them a score based on secondary features
        for tutor in tutor_list:
                print tutor
                if tutor["complete"] == 1:
                        match_score = 0.0
                        email = tutor['email']
                        addresses = []
                        #find the days for which addresses work
                        try:
                                tutee_loc = form["0-address"]
                                print tutor
                        
                                tutee_address = session[tutee_loc.capitalize() + "_Address"]
                                print tutee_address
                                        
                                tutee_start = float(form["0-start_hour"]) + (float(form["0-start_minute"]) * .01)
                                if form["0-start_type"] == "PM":
                                        tutee_start += 12

                                        

                                tutee_end = float(form["0-end_hour"]) + (float(form["0-end_minute"]) * .01)
                                if form["0-end_type"] == "PM":
                                        tutee_end += 12
                                               
                                       
                                best_time = -99999
                                for d in tutor['days'][day]:
                                        distances = []
                                        print d['addresses']
                                        for a in d['addresses']:
                                                tutor_address = tutor[a.capitalize() + "_Address"]
                                                print tutor_address
                                                dist = 0.0
                                                if (tutor_address["zipcode"] == tutee_address["zipcode"]):
                                                        dist += 4.0
                                                distance = calculate_distance(tutor_address, tutee_address)
                                                dist += float(3 - distance)
                                                distances.append(dist)
                                        print distances
                                        score = max(distances)
                                        

                                        tutor_start = float(d["start_hour"]) + (float(d["start_min"]) *.01)
                                        if d["start_type"] == "PM":
                                                tutor_start += 12
                                        
                                        tutor_end = float(d["end_hour"]) + (float(d["end_min"]) *.01)
                                        if d["end_type"] == "PM":
                                                tutor_end += 12 

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
