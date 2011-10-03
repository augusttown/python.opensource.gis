# saveAsText.py
import os
#import shutil
from osgeo import ogr

#===============================================================================
# if os.path.exists("country-wkt-files"):
#    shutil.rmtree("country-wkt-files")
# os.mkdir("country-wkt-files")
#===============================================================================

# set the working directory so you don't have to type in path later
os.chdir("E:/projects/python.opengis")
# ESRI shape file driver
driver = ogr.GetDriverByName("ESRI Shapefile")

shapefile = ogr.Open("dataset/TM_WORLD_BORDERS-0.3.shp")
layer = shapefile.GetLayer(0)

for i in range(layer.GetFeatureCount()):
    feature = layer.GetFeature(i)
    name = feature.GetField("NAME")
    geometry = feature.GetGeometryRef()

    #f = file(os.path.join("country-wkt-files", name + ".txt"), "w")
    dstPath = "scratch/country-wkt-files.txt"
    if os.path.exists(dstPath):
        os.remove(dstPath)
    
    f = file(dstPath, "w")    
    f.write(geometry.ExportToWkt())
    f.close()