# calcBorderLength.py
import os
import osgeo.ogr
import pyproj

def getLineSegmentsFromGeometry(geometry):
    segments = []
    if geometry.GetPointCount() > 0:
        segment = []
        for i in range(geometry.GetPointCount()):
            segment.append(geometry.GetPoint_2D(i))
        segments.append(segment)
    for i in range(geometry.GetGeometryCount()):
        subGeometry = geometry.GetGeometryRef(i)
        segments.extend(
            getLineSegmentsFromGeometry(subGeometry))
    return segments

# set the working directory so you don't have to type in path later
os.chdir("E:/projects/python.opengis")
# ESRI shape file driver
driver = osgeo.ogr.GetDriverByName("ESRI Shapefile")
# load the shapefile
shapefile = driver.Open("dataset/common-border.shp", 0)
layer = shapefile.GetLayer(0)

feature = layer.GetFeature(0)
geometry = feature.GetGeometryRef()
segments = getLineSegmentsFromGeometry(geometry)

# calculate geodetic distance between two points
#  create pyproj.Geod instance to do the geodetic calculation
#  you must give the datum, e.g. "WGS84" 
geod = pyproj.Geod(ellps='WGS84')

totLength = 0.0
for segment in segments:
    for i in range(len(segment)-1):
        pt1 = segment[i]
        pt2 = segment[i+1]

        long1,lat1 = pt1
        long2,lat2 = pt2
        # geod.inv() the inverse geodetic transformation method
        angle1,angle2,distance = geod.inv(long1, lat1, long2, lat2)
        totLength += distance

print "Total border length = %0.2f km" % (totLength/1000)

