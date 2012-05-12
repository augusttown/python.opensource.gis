# import modules
import os
import sys
# import gdal/ogr modules
from osgeo import ogr
from osgeo import osr

# set current workspace

# call  C:\yingqi\sazabi\programs\osgeo4w\osgeo4w.bat to set environment
os.system('C:/yingqi/sazabi/programs/osgeo4w/osgeo4w.bat')

#wfsUrl = WFS:http://gouf:6080/arcgis/services/playground/haiti_3857/MapServer/WFSServer

#
os.system('ogrinfo -ro http://gouf:6080/arcgis/services/playground/haiti_3857/MapServer/WFSServer?SERVICE=WFS')
#os.system('ogrinfo -ro WFS:http://gouf:6080/arcgis/services/playground/haiti_3857/MapServer/WFSServer')

#
#os.system('ogrinfo -ro http://gouf:6080/arcgis/services/playground/haiti_3857/MapServer/WFSServer?SERVICE=WFS ')

