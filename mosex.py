import urllib
import csv
import time
import os
from geopy import geocoders
from geopy.geocoders.google import GQueryError
#from pysqlite2 import dbapi2 as sqlite3
#from sqlite3 import dbapi2 as sqlite3
import sqlite3


countiesicareabout = ['Cole', 'Osage', 'Callaway', 'Boone', 'Moniteau',
'Miller', 'Maries']

urlroot = 'http://www.mshp.dps.missouri.gov/MSHPWeb/PatrolDivisions/CRID/SOR/data/'

def fetchdata():
        print "Downloading 8 files total, maybe 12mb combined."
        urllib.urlretrieve(urlroot + "name.csv", './monames.csv')
        print "Files completed: 1,",
        urllib.urlretrieve(urlroot + "address.csv", './moaddress.csv') 
        print "2,",
        urllib.urlretrieve(urlroot + "birthdate.csv", './mobirthdate.csv')        
        print "3,",
        urllib.urlretrieve(urlroot + "offense.csv", './mooffense.csv') 
        print "4,",
        urllib.urlretrieve(urlroot + "photo.csv", './mophoto.csv')        
        print "5,",
        urllib.urlretrieve(urlroot + "physdsc.csv", './mophysdsc.csv') 
        print "6,",
        urllib.urlretrieve(urlroot + "scars_marks_tattoos.csv", './moscars.csv')        
        "7,",
        urllib.urlretrieve(urlroot + "victim.csv", './movictim.csv') 
        print "8. All files downloaded."

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



# OK, now let's fire up our address database
geodbconn = sqlite3.connect('./geodb.sqlite')
geodb = geodbconn.cursor()
# Do we have a table? If not, we'll need to create one.
geodb.execute('''select count(*) from sqlite_master where type='table' and name='sexgeo';''')
sqlreturn = geodb.fetchone()
if sqlreturn[0] == 0:
    geodb.execute('''create table sexgeo (fulladdy text, glat text, glong text)''')
    geodb.execute('''create index addyindex on sexgeo (fulladdy)''')   
geodbconn = sqlite3.connect('./geodb.sqlite')
geodb = geodbconn.cursor()
geodb.execute('''select count(*) from sqlite_master where type='table' and name='sexgeo';''')
sqlreturn = geodb.fetchone()
if sqlreturn[0] == 0:
    geodb.execute('''create table sexgeo (fulladdy text, glat text, glong text)''')
    geodb.execute('''create index addyindex on sexgeo (fulladdy)''')   


# OK, now we have to start (re)building our main perp database.
if os.path.exists('./perpdb.sqlite'):
        os.remove('./perpdb.sqlite')

perpdbconn = sqlite3.connect('./perpdb.sqlite')
perpdb = perpdbconn.cursor()
perpdb.execute('''create table perp (ID text, addytype text, addyname text,
streetno text, streetname text, city text, state text, zipcode text,
county text)''')
perpdb.execute('''create index idindex on perp (ID)''')

####DO I WANT TO PICK UP THE NAMES HERE?


localcsv = csv.reader(open(r'./sor.csv','r'))
localcsv.next()                             #Skip header row

for line in localcsv:

    for idx, val in enumerate(line):
        line[idx] = val.title().strip();

    line[12] = line[12].upper()         #Fix one state    












