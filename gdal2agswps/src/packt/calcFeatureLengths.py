# calcFeatureLengths.py
#import sys
import os
import pyproj

from osgeo import osr
from osgeo import ogr 

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

#===============================================================================
# if len(sys.argv) != 2:
#    print "Usage: calcFeatureLengths.py <shapefile>"
#    sys.exit(1)
#===============================================================================

#filename = sys.argv[1]

# set the working directory so you don't have to type in path later
os.chdir("E:/projects/python.opengis")
# ESRI shape file driver
driver = ogr.GetDriverByName("ESRI Shapefile")
# open shapefile
shapefile = driver.Open("dataset/common-border.shp", 0)
layer = shapefile.GetLayer(0)
# get the coordinate system
spatialRef = layer.GetSpatialRef()
if spatialRef == None:
    print "Shapefile lacks a spatial reference, using WGS84."
    spatialRef = osr.SpatialReference()
    spatialRef.SetWellKnownGeogCS('WGS84')

if spatialRef.IsProjected():
    srcProj = pyproj.Proj(spatialRef.ExportToProj4())
    dstProj = pyproj.Proj(proj='longlat', ellps='WGS84',
                          datum='WGS84')

for i in range(layer.GetFeatureCount()):
    # get segments from features
    feature = layer.GetFeature(i)
    geometry = feature.GetGeometryRef()
    segments = getLineSegmentsFromGeometry(geometry)
    
    # calculate geodetic distance between two points
    #  create pyproj.Geod instance to do the geodetic calculation
    #  you must give the datum, e.g. "WGS84" 
    geod = pyproj.Geod(ellps='WGS84')

    totLength = 0.0
    for segment in segments:
        for j in range(len(segment)-1):
            pt1 = segment[j]
            pt2 = segment[j+1]

            long1,lat1 = pt1
            long2,lat2 = pt2

            if spatialRef.IsProjected():
                long1,lat1 = pyproj.transform(srcProj, dstProj, long1, lat1)
                long2,lat2 = pyproj.transform(srcProj, dstProj, long2, lat2)
                
            try:
                angle1,angle2,distance = geod.inv(long1, lat1, long2, lat2)
            except ValueError:
                print "Unable to calculate distance from " + "%0.4f,%0.4f to %0.4f,%0.4f" % (long1, lat1, long2, lat2)
                distance = 0.0
            totLength += distance

    print "Total length of feature %d is %0.2f km" \
        % (i, totLength/1000)
