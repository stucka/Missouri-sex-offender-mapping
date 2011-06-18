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
perpdb.execute('''create table perp (ID integer, addytype text, addyname text,
streetno text, streetname text, city text, state text, zipcode text,
county text, shortaddy text, fulladdy text, glat text, glong text)''')
perpdb.execute('''create index idindex on perp (ID)''')

####DO I WANT TO PICK UP THE NAMES HERE?


localcsv = csv.reader(open(r'./moaddress.csv','r'))
#localcsv.next()                             #Skip header row

for line in localcsv:
    line[9] = line[9].title().strip()
## Is this in a place we actually care about?
    if not (line[7] == 'MO' and line[9] in countiesicareabout):
#        print "OK, I'm ignoring ", line[0], ": at",fulladdy
#        print ".",
        pass
    else:
        print "Got one!"
        for idx, val in enumerate(line):
            line[idx] = val.title().strip();
        line[7] = line[7].upper()
#perpdb.execute('''create table perp (ID integer, addytype text, addyname text,
#streetno text, streetname text, city text, state text, zipcode text,
#county text, shortaddy text, fulladdy text, glat text, glong text)''')
#So insert's going to look like line0, line2, line 3, line4,
#line5, line 6, line7, line8, line9, shortaddy, fulladdy, glat, glong
#So let's start getting those values
#Do we take names from here or the name table?



        if len(line[9]) > 2:
            CountyTextFix = line[9] + " County, "
            CountyNameFix = line[9] + " County"
        else:
            CountyTextFix = ''
            CountyNameFix = ''

        if len(line[3]) > 2:
            PlaceNameFix = line[3] + ", "
        else:
            PlaceNameFix = ""
            
        shortaddy = PlaceNameFix + line[4] + " " + line[5] + ", " + line[6]
        fulladdy = shortaddy + ", " + CountyTextFix + line[7] + " " + line[8]
        

##
## OK, so let's see if we already know where this address is. We can
## check to see how many times the row shows up; if the row doesn't exist in
## the database, we'll need to try geocoding it through Google, and if that
## doesn't work we'll go through Geocoder.US, and if that doesn't work
## we'll give it the site of the 1903 RMS Republic wreck for no reason
## whatsoever.
## If we do have a single listing, let's grab the lat and long.
## If we have multiple listings for the same address, we probably have
## database corruption.

        geodb.execute('select count(*), glat, glong from sexgeo where fulladdy = ?', [fulladdy])
        sqlreturn = geodb.fetchone()
    #    print sqlreturn
        if sqlreturn[0] == 0:
            try:
                googlegeo = geocoders.Google()
                for tempplace, (templat, templong) in googlegeo.geocode(fulladdy, exactly_one=False):
                    gplace=str(tempplace)
                    glat=str(templat)
                    glong=str(templong)
            except (ValueError, GQueryError):
                try:
                    usgeo = geocoders.GeocoderDotUS()
                    for tempplace, (templat, templong) in usgeo.geocode(fulladdy, exactly_one=False):
                        gplace=str(tempplace)
                        glat=str(templat)
                        glong=str(templong)
                except (ValueError, GQueryError, TypeError):
                    print "Location '", fulladdy, "not found. Setting lat-long to 42.02,-42.02, in honor of OCGA 42 1 12"
                    glat = "42.02"
                    glong = "-42.02"
                    gplace = "OCGA 42-1-12 calls for registry, but we can't find this person."
    ## So if things went right, we now have a geocoded address.
    ## Let's put that in the database.                
            geodb.execute('insert into sexgeo values (?,?,?)', [fulladdy, glat, glong])
            geodbconn.commit()
            print line[0], ": geocoded and recorded ", fulladdy, "at ", glat, ", ", glong
        elif sqlreturn[0] == 1:
            glat = str(sqlreturn[1])
            glong = str(sqlreturn[2])
#            print line[0], ": at",fulladdy, " already in database at ", glat, "and", glong
            print line[0], " already in database"
        else:
            print "Multiple rows for same ", fulladdy, ", What the hell did you do?"



"""
monames file layout (educated guesses, unconfirmed)
0 - ID
1 - ?
2 - H/W/N (home or work or something)
3 - Placename name
4 - StreetNo
5 - StreetName
6 - CityName
7 - StateName
8 - ZIP
9 - County
10 - Last Name?
11 - First Name?
12 - Middle Name?
13 - Jr. Sr maybe?
14 - ?
15 - ?
"""









