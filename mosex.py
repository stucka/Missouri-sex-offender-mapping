import urllib
import csv
import time
import os
from geopy import geocoders
from geopy.geocoders.google import GQueryError
#from pysqlite2 import dbapi2 as sqlite3
#from sqlite3 import dbapi2 as sqlite3
import sqlite3


#countiesicareabout = ['Bibb', 'Monroe', 'Houston', 'Jones', 'Peach',
#'Crawford', 'Twiggs', 'Wilkinson', 'Laurens', 'Bleckley', 'Baldwin']


urlroot = 'http://www.mshp.dps.missouri.gov/MSHPWeb/PatrolDivisions/CRID/SOR/data/'

def fetchdata():
        urllib.urlretrieve(urlroot + "name.csv", './monames.csv')        
        urllib.urlretrieve(urlroot + "address.csv", './moaddress.csv') 
        urllib.urlretrieve(urlroot + "birthdate.csv", './mobirthdate.csv')        
        urllib.urlretrieve(urlroot + "offense.csv", './mooffense.csv') 
        urllib.urlretrieve(urlroot + "photo.csv", './mophoto.csv')        
        urllib.urlretrieve(urlroot + "physdsc.csv", './mophysdsc.csv') 
        urllib.urlretrieve(urlroot + "scars_marks_tattoos.csv", './moscars.csv')        
        urllib.urlretrieve(urlroot + "victim.csv", './movictim.csv') 

try:
#    deltatime = time.time() - os.path.getmtime('./monames.csv')
    if time.time() - os.path.getmtime('./monames.csv') > 60 * 60 * 24 * 6:   #If file is older than six days
        print "Old file found. Updating."
        fetchdata()
    else:
        print "You have the newest file. No need to do processing."
#        import sys
#        sys.exit()    #die if needed
except (ValueError, os.error):
    print "No file found: ./monames.csv ... downloading now."
    fetchdata()




