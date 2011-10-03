# changeDatum.py
import os
#import shutil
from osgeo import ogr
from osgeo import osr
#from osgeo import gdal

# Define the source and destination datums, and a
# transformation object to convert from one to the other.
srcDatum = osr.SpatialReference()
srcDatum.SetWellKnownGeogCS('NAD27')

dstDatum = osr.SpatialReference()
dstDatum.SetWellKnownGeogCS('WGS84')

transform = osr.CoordinateTransformation(srcDatum, dstDatum)

# set the working directory so you don't have to type in path later
os.chdir("E:/projects/python.opengis")
# ESRI shape file driver
driver = ogr.GetDriverByName("ESRI Shapefile")

# Open the source shapefile.
#srcFile = ogr.Open("dataset/tgr02020lkA.shp")
srcFile = driver.Open("dataset/tgr02020lka.shp", 0)
srcLayer = srcFile.GetLayer(0)

# Create the dest shapefile, and give it the new projection.
dstPath = 'scratch/lka_reprojected.shp'
if os.path.exists(dstPath):
    # this .prj, .shx, .dbf and .shp that are associated with same shapefile
    driver.DeleteDataSource(dstPath)

#===============================================================================
# if os.path.exists("lkA-reprojected"):
#    shutil.rmtree("lkA-reprojected")
# os.mkdir("lkA-reprojected")
# dstPath = os.path.join("lkA-reprojected", "lkA02020.shp")
#===============================================================================

dstFile = driver.CreateDataSource(dstPath)
dstLayer = dstFile.CreateLayer("lka_reprojected", dstDatum)

# Reproject each feature in turn.
for i in range(srcLayer.GetFeatureCount()):
    feature = srcLayer.GetFeature(i)
    geometry = feature.GetGeometryRef()

    newGeometry = geometry.Clone()
    newGeometry.Transform(transform)

    feature = ogr.Feature(dstLayer.GetLayerDefn())
    feature.SetGeometry(newGeometry)
    dstLayer.CreateFeature(feature)
    feature.Destroy()

# All done.
srcFile.Destroy()
dstFile.Destroy()