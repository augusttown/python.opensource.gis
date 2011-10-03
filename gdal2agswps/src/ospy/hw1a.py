# import modules
import os, sys
from osgeo import ogr


# set the working directory so you don't have to type in path later
os.chdir('E:\documents\projects\ospy.2009\ospy_data1')

# open the output text file for writing
#file = open('output.txt', 'w')

# get the shapefile driver
driver = ogr.GetDriverByName('ESRI Shapefile')

# open the data source
datasource = driver.Open('sites.shp', 0)    # open shapefile readonly
#datasource = driver.Open('sites_copy.shp', 0)    # open shapefile readonly
if datasource is None:
    print 'Could not open file'
    sys.exit(1)

# get the data layer
layer = datasource.GetLayer()
# get layer name
print layer.GetName()


# loop through the features in the layer
feature = layer.GetNextFeature()
while feature:

    # get the attributes
    id = feature.GetFieldAsString('id')
    cover = feature.GetFieldAsString('cover')

    # get the x,y coordinates for the point
    geom = feature.GetGeometryRef()
    x = str(geom.GetX())
    y = str(geom.GetY())

    # write info out to the text file
    #file.write(id + ' ' + x + ' ' + y + ' ' + cover + '\n')
    
    # print out info in console
    print x + "," + y

    # destroy the feature and get a new one
    feature.Destroy()
    feature = layer.GetNextFeature()

# close the data source and text file
datasource.Destroy()
#file.close()