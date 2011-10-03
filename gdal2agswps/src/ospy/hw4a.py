# import system modules
import os, sys
# import gdal related modules
try:
    from osgeo import ogr
    from osgeo import gdal
    from osgeo.gdalconst import *
    os.chdir(r'E:\documents\projects\ospy.2009')
except ImportError:
    import ogr, gdal
    from gdalconst import *
    os.chdir(r'E:\documents\projects\ospy.2009')

# open the shapefile and get the layer
driver = ogr.GetDriverByName('ESRI Shapefile')
# the path can either be r"" or just ""
shp = driver.Open(r'ospy_data4\sites.shp')
if shp is None:
    print 'Could not open sites.shp'
    sys.exit(1)

shpLayer = shp.GetLayer()
print shpLayer.GetName()

# register all of the GDAL drivers
gdal.AllRegister()

# open the image
# the path must be r"", otherwise it doesn't recognize the file path
img = gdal.Open(r'ospy_data4\aster.img', GA_ReadOnly)
if img is None:
    print 'Could not open aster.img'
    sys.exit(1)

# get image size
rows = img.RasterYSize
cols = img.RasterXSize
bands = img.RasterCount

print 'rows: ' + str(rows)
print 'cols: ' + str(cols)
print 'bands: ' + str(bands)

# get georeference info
transform = img.GetGeoTransform()

xOrigin = transform[0]
yOrigin = transform[3]
pixelWidth = transform[1]
pixelHeight = transform[5]

# loop through the features in the shapefile
feat = shpLayer.GetNextFeature()
while feat:
    geom = feat.GetGeometryRef()
    x = geom.GetX()
    y = geom.GetY()

    # compute pixel offset
    xOffset = int((x - xOrigin) / pixelWidth)
    yOffset = int((y - yOrigin) / pixelHeight)

    # create a string to print out
    s = feat.GetFieldAsString('ID') + ' '

    # loop through the bands
    for j in range(bands):
        band = img.GetRasterBand(j+1) # 1-based index
        # read data and add the value to the string
        # this crashes
        #data = band.ReadAsArray(xOffset, yOffset, 1, 1)
        #value = data[0, 0]
        
        # this works
        data = band.ReadAsArray(0, 0, cols, rows)        
        value = data[xOffset, yOffset]
        
        s = s + str(value) + ' '

    # print out the data string
    print s
    # get the next feature
    feat.Destroy()
    feat = shpLayer.GetNextFeature()

# close the shapefile
shp.Destroy()
    