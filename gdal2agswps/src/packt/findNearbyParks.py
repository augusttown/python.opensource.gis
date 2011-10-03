# findNearbyParks.py
import os
from osgeo import ogr
import shapely.geometry
import shapely.wkt

# set the working directory so you don't have to type in path later
os.chdir("E:/projects/python.opengis")
# ESRI shape file driver
driver = ogr.GetDriverByName("ESRI Shapefile")

#
MAX_DISTANCE = 0.1 # Angular distance; approx 10 km.
#
print "Loading urban areas..."

urbanAreas = {} # Maps area name to Shapely polygon.
#===============================================================================
#shapefile = ogr.Open("dataset/tl_2009_06_cbsa.shp")
# layer = shapefile.GetLayer(0)
#===============================================================================
shapefile = driver.Open("dataset/tl_2009_06_cbsa.shp")
# TODO: error handling
layer = shapefile.GetLayer(0)

for i in range(layer.GetFeatureCount()):
    feature = layer.GetFeature(i)
    name = feature.GetField("NAME")
    geometry = feature.GetGeometryRef()
    shape = shapely.wkt.loads(geometry.ExportToWkt())
    dilatedShape = shape.buffer(MAX_DISTANCE)
    urbanAreas[name] = dilatedShape
    feature.Destroy()

print "Checking parks..."

f = file("dataset/CA_Features_20101203.txt", "r")
for line in f.readlines():
    chunks = line.rstrip().split("|")
    if chunks[2] == "Park":
        parkName = chunks[1]
        latitude = float(chunks[9])
        longitude = float(chunks[10])
        print str(longitude) + "," + str(latitude) 
        
        pt = shapely.geometry.Point(longitude, latitude)
        # for each (key, value) parit in urbanAreas.items()
        #   Q: what datastructure os urbanArea?
        for urbanName,urbanArea in urbanAreas.items():
            if urbanArea.contains(pt):
                print parkName + " is in or near " + urbanName
f.close()

shapefile.Destroy()
