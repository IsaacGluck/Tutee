import urllib2
import json

##GOOGLE API KEY
google_key = 'AIzaSyBun2m9jaQTFGb0qtR7Shh7inqFhzKbLL4' #API key

#location takes an address, and using the google maps api returns the zip code and longditude/ latitude
def locate(address):
    address = address.replace(" ", "%20") #needed for proper api usage
    url = "https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s" % (address, google_key)

    request = urllib2.urlopen(url)
    results = request.read()
    google_dict = json.loads(results)["results"][0] #gives dictionary form of responses

    long_lat = google_dict["geometry"]["location"] #dictionary with keys lat and lng
    lng = long_lat["lng"] #longitude
    lat = long_lat["lat"] #latitude

    zipcode = google_dict["address_components"][8]["long_name"] #in array a_c, slot 8 is a dict with key long_name, the zip code

    return [lng, lat, zipcode]
