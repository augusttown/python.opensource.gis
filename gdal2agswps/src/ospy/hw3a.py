# import modules
import os, sys
from osgeo import ogr

# set the working directory
os.chdir('E:/documents/projects/ospy.2009')

# get the shapefile driver
driver = ogr.GetDriverByName('ESRI Shapefile')

# open sites.shp and get the layer
sitesDS = driver.Open('ospy_data3/sites.shp', 0)
if sitesDS is None:
    print 'Could not open sites.shp'
    sys.exit(1)
sitesLayer = sitesDS.GetLayer()

# open cache_towns.shp and get the layer
townsDS = driver.Open('ospy_data3/cache_towns.shp', 0)
if townsDS is None:
    print 'Could not open cache_towns.shp'
    sys.exit(1)
townsLayer = townsDS.GetLayer()

# use an attribute filter to restrict cache_towns.shp to "Nibley"
# create more like a virtual layer with a SQL like expression
townsLayer.SetAttributeFilter("NAME = 'Nibley'")

#townFeature = townsLayer.GetNextFeature()
#while townFeature:
#    townName = townFeature.GetFieldAsString('NAME')
#    print townName
#    townFeature.Destroy()
#    townFeature = townsLayer.GetNextFeature()

# Q: after looping through the features, how set the cursor back to beginning?
    
# GetFeature(0) seems return the first of the whole feature set instead of filtered feature set
#nibleyFeature = townsLayer.GetFeature(0)
# GetNextFeature() returns the Nibley geometry and buffer it by 1500
nibleyFeature = townsLayer.GetNextFeature()
#print nibleyFeature.GetField('NAME')
print nibleyFeature.GetFieldAsString('NAME')

nibleyGeom = nibleyFeature.GetGeometryRef()
# !!! it crashed somehow here !!!
bufferGeom = nibleyGeom.Buffer(1500)

# use bufferGeom as a spatial filter on sites.shp to get all sites
# within 1500 meters of Nibley
# this probably means intersect spatial filter
sitesLayer.SetSpatialFilter(bufferGeom)

# loop through the remaining features in sites.shp and print their
# id values
siteFeature = sitesLayer.GetNextFeature()
while siteFeature:
    #print siteFeature.GetField('ID')
    print siteFeature.GetFieldAsString('ID')
    siteFeature.Destroy()
    siteFeature = sitesLayer.GetNextFeature()

# close the shapefiles
sitesDS.Destroy()
townsDS.Destroy()