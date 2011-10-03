# calcCommonBorders.py
import os
#import shutil
# import gdal modules
from osgeo import ogr
from osgeo import osr
# import shapely modules
import shapely.wkt

# set the working directory so you don't have to type in path later
os.chdir("E:/projects/python.opengis")
# ESRI shape file driver
driver = ogr.GetDriverByName("ESRI Shapefile")

# Load the thai and myanmar polygons from the world borders
# dataset.
shapefile = ogr.Open("dataset/TM_WORLD_BORDERS-0.3.shp")
layer = shapefile.GetLayer(0)

thailand = None
myanmar = None

for i in range(layer.GetFeatureCount()):
    feature = layer.GetFeature(i)
    if feature.GetField("ISO2") == "TH":
        geometry = feature.GetGeometryRef()
        # assume there is on thailand feature
        thailand = shapely.wkt.loads(geometry.ExportToWkt())
    elif feature.GetField("ISO2") == "MM":
        geometry = feature.GetGeometryRef()
        # assume there is on myanmar feature
        myanmar = shapely.wkt.loads(geometry.ExportToWkt())

# Calculate the common border.
commonBorder = thailand.intersection(myanmar)

# Save the common border into a new shapefile.
#===============================================================================
# if os.path.exists("common-border"):
#    shutil.rmtree("common-border")
# os.mkdir("common-border")
#===============================================================================

dstPath = "scratch/common-border.shp"
if os.path.exists(dstPath):
    # this .prj, .shx, .dbf and .shp that are associated with same shapefile
    driver.DeleteDataSource(dstPath)

spatialReference = osr.SpatialReference()
spatialReference.SetWellKnownGeogCS("WGS84")

dstFile = driver.CreateDataSource(dstPath)
dstLayer = dstFile.CreateLayer("common-border", spatialReference)

wkt = shapely.wkt.dumps(commonBorder)

feature = ogr.Feature(dstLayer.GetLayerDefn())
feature.SetGeometry(ogr.CreateGeometryFromWkt(wkt))
dstLayer.CreateFeature(feature)

feature.Destroy()
dstFile.Destroy()