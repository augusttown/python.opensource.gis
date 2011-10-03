# findShoshone.py
import os
import pyproj

distance = 132.7 * 1000
angle    = 270.0

# set the working directory so you don't have to type in path later
os.chdir("E:/projects/python.opengis")

f = file("dataset/CA_Features_20101203.txt", "r")
for line in f.readlines():
    chunks = line.rstrip().split("|")
    if chunks[1] == "Shoshone" and chunks[2] == "Populated Place":
        latitude = float(chunks[9])
        longitude = float(chunks[10])
        # calculate geodetic distance between two points
        #  create pyproj.Geod instance to do the geodetic calculation
        #  you must give the datum, e.g. "WGS84" 
        geod = pyproj.Geod(ellps='WGS84')
        # Geod.fwd() to calculate the forward geodetic transformation
        newLong,newLat,invAngle = geod.fwd(longitude, latitude, angle, distance)

        print "Shoshone is at %0.4f,%0.4f" % (latitude, longitude)
        print "The point %0.2f km west of Shoshone " % (distance/1000.0) + "is at %0.4f, %0.4f" % (newLat, newLong)

f.close()

