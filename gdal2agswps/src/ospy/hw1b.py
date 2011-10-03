# import standard modules
import os, sys
# import gdal/ogr module
from osgeo import ogr

# set the working directory
os.chdir('E:\documents\projects\ospy.2009')
# get the shapefile driver
driver = ogr.GetDriverByName('ESRI Shapefile')

# open the input data source and get the layer
inDS = driver.Open('ospy_data1\sites.shp', 0)
if inDS is None:
    print 'Could not open file'
    sys.exit(1)
inLayer = inDS.GetLayer()

# create a new data source and layer
fn = 'ospy_data1\sites_copy.shp'
if os.path.exists(fn):              # test if file already exists
    driver.DeleteDataSource(fn)     # if exists, delete it
outDS = driver.CreateDataSource(fn) # create new data source

if outDS is None:
    print 'Could not create file'
    sys.exit(1)
outLayer = outDS.CreateLayer('sites_copy', geom_type=ogr.wkbPoint)

# get the FieldDefn's for the id and cover fields in the input shapefile
feature = inLayer.GetFeature(0)
idFieldDefn = feature.GetFieldDefnRef('id')             # get reference of field 'id'
coverFieldDefn = feature.GetFieldDefnRef('cover')       # get reference of field 'cover'

# create new id and cover fields in the output shapefile
outLayer.CreateField(idFieldDefn)                       # create new field from existing field reference
outLayer.CreateField(coverFieldDefn)                    # create new field from existing field reference

# get the FeatureDefn for the output layer
featureDefn = outLayer.GetLayerDefn()

# loop through the input features
inFeature = inLayer.GetNextFeature()
while inFeature:
    # get the cover attribute for the input feature
    cover = inFeature.GetField('cover')
    # check to see if cover == grass
    if cover == 'trees':
        # create a new feature
        outFeature = ogr.Feature(featureDefn)

        # set the geometry
        geom = inFeature.GetGeometryRef()
        outFeature.SetGeometry(geom)
    
        # set the attributes
        id = inFeature.GetField('id')
        outFeature.SetField('id', id)
        outFeature.SetField('cover', cover)
    
        # add the feature to the output layer
        outLayer.CreateFeature(outFeature)
    
        # destroy the output feature
        outFeature.Destroy()

    # destroy the input feature and get a new one
    inFeature.Destroy()
    inFeature = inLayer.GetNextFeature()

# close the data sources
inDS.Destroy()
outDS.Destroy()