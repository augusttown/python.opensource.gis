# changeProjection.py
import os
#import os.path
#import shutil           # modules for high level file operations
from osgeo import ogr
from osgeo import osr
#from osgeo import gdal

# Define the source and destination projections, and a
# transformation object to convert from one to the other.
#===============================================================================
# srcProjection = osr.SpatialReference()
# srcProjection.SetUTM(17)
#===============================================================================

# Here is the code from http://www.gdal.org/ogr/osr_tutorial.html
#   that creates a UTM Zone 17 projected coordinate system
#   and associate it with WGS84 GCS
srcProjection = osr.SpatialReference()
srcProjection.SetProjCS("UTM 17 (NAD83) in Northern Hemisphere.");
srcProjection.SetWellKnownGeogCS("NAD83");
srcProjection.SetUTM(17, True);    # True as Northern Hemisphere

# Define the target and destination projections
dstProjection = osr.SpatialReference()
dstProjection.SetWellKnownGeogCS("WGS84")

# create transformation
transform = osr.CoordinateTransformation(srcProjection, dstProjection)

# set the working directory so you don't have to type in path later
os.chdir("E:/projects/python.opengis")
# ESRI shape file driver
driver = ogr.GetDriverByName("ESRI Shapefile")

# Open the source shapefile.
#srcFile = ogr.Open("dataset/miami.shp")
# Or open shape file as data source
#   Q: what's the difference between ogr.Open() and driver.Open()?
srcFile = driver.Open("dataset/miami.shp", 0)
# get layer 
srcLayer = srcFile.GetLayer(0)

# Create the dest shapefile, and give it the new projection.
#dstPath = os.path.join("miami-reprojected", "miami.shp")
dstPath = 'scratch/miami_reprojected.shp'
if os.path.exists(dstPath):
    # this .prj, .shx, .dbf and .shp that are associated with same shapefile
    driver.DeleteDataSource(dstPath)

dstFile = driver.CreateDataSource(dstPath)
dstLayer = dstFile.CreateLayer("miami_reprojected", dstProjection)

# Reproject each feature in turn.
for i in range(srcLayer.GetFeatureCount()):
    feature = srcLayer.GetFeature(i)
    geometry = feature.GetGeometryRef()
    # clone geometry instance and set it to new feature
    newGeometry = geometry.Clone()
    newGeometry.Transform(transform)

    feature = ogr.Feature(dstLayer.GetLayerDefn())
    feature.SetGeometry(newGeometry)
    dstLayer.CreateFeature(feature)
    feature.Destroy()

# All done.
srcFile.Destroy()
dstFile.Destroy()
