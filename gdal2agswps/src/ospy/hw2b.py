# import modules
import os, sys
from osgeo import ogr
from osgeo import osr

# set the working directory
os.chdir('E:/documents/projects/ospy.2009')

# get the shapefile driver
driver = ogr.GetDriverByName('ESRI Shapefile')

# create the input SpatialReference
inSpatialRef = osr.SpatialReference()
inSpatialRef.ImportFromEPSG(4269)

# create the output SpatialReference
outSpatialRef = osr.SpatialReference()
outSpatialRef.ImportFromEPSG(26912)

# create the CoordinateTransformation
coordTrans = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)

# open the input data source and get the layer
inDS = driver.Open('ospy_data2/ut_counties.shp', 0)
if inDS is None:
    print 'Could not open file'
    sys.exit(1)
inLayer = inDS.GetLayer()

# create a new data source and layer
fn = 'ospy_data2/ut_counties_porjected.shp'
if os.path.exists(fn):
    driver.DeleteDataSource(fn)
outDS = driver.CreateDataSource(fn)
if outDS is None:
    print 'Could not create file'
    sys.exit(1)
outLayer = outDS.CreateLayer('ut_counties_porjected', geom_type=ogr.wkbPolygon)

# get the FieldDefn for the county name field
feature = inLayer.GetFeature(0)
fieldDefn = feature.GetFieldDefnRef('name')
# add the field to the output shapefile
outLayer.CreateField(fieldDefn)
# get the FeatureDefn for the output shapefile
featureDefn = outLayer.GetLayerDefn()

# loop through the input features
inFeature = inLayer.GetNextFeature()
while inFeature:
    # get the input geometry
    geom = inFeature.GetGeometryRef()
    # reproject the geometry
    geom.Transform(coordTrans)
    # create a new feature
    outFeature = ogr.Feature(featureDefn)
    # set the geometry and attribute
    outFeature.SetGeometry(geom)
    outFeature.SetField('name', inFeature.GetField('name'))
    # add the feature to the shapefile
    outLayer.CreateFeature(outFeature)
    # destroy the features and get the next input feature
    outFeature.Destroy
    inFeature.Destroy
    inFeature = inLayer.GetNextFeature()

# close the shapefiles
inDS.Destroy()
outDS.Destroy()

# create the *.prj file
outSpatialRef.MorphToESRI()     # the output projection string will be in ESRI syntax
file = open('ospy_data2/ut_counties_porjected.prj', 'w')
file.write(outSpatialRef.ExportToWkt())
file.close()
