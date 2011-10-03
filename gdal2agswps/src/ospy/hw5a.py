# create an NDVI
import os, sys
import numpy
#import hw5a_util
from osgeo import gdal 
#from osgeo.gdalconst import *
from osgeo.gdalconst import GA_ReadOnly
from osgeo.gdalconst import GDT_Float32

# set home directory
os.chdir(r'E:\documents\projects\ospy.2009')
# register all of the GDAL drivers
gdal.AllRegister()

# open the image
inDs = gdal.Open(r'ospy_data5\aster.img', GA_ReadOnly)
if inDs is None:
    print 'Could not open aster.img'
    sys.exit(1)

# get image size
rows = inDs.RasterYSize
cols = inDs.RasterXSize
bands = inDs.RasterCount

# get the bands and block sizes
inBand2 = inDs.GetRasterBand(2)
inBand3 = inDs.GetRasterBand(3)

# GetBlockSize doesn't work
#blockSizes = hw5a_util.GetBlockSize(inBand2)
#xBlockSize = blockSizes[0]
#yBlockSize = blockSizes[1]

# use ERDAS default block size 64x64
xBlockSize = 64
yBlockSize = 64

print yBlockSize, xBlockSize

# create the output image
driver = inDs.GetDriver()
outDs = driver.Create(r'ospy_data5\ndvi.img', cols, rows, 1, GDT_Float32)
if outDs is None:
    print 'Could not create ndvi.img'
    sys.exit(1)
outBand = outDs.GetRasterBand(1)


# read and write raster by blocks
# loop through the rows
#===============================================================================
# for i in range(0, rows, yBlockSize):
#    if i + yBlockSize < rows:
#        numRows = yBlockSize
#    else:
#        numRows = rows - i
# 
#    # loop through the columns
#    for j in range(0, cols, xBlockSize):
#        if j + xBlockSize < cols:
#            numCols = xBlockSize
#        else:
#            numCols = cols - j
# 
#    # read the data in
#    data2 = inBand2.ReadAsArray(j, i, numCols, numRows).astype(numpy.float)
#    data3 = inBand3.ReadAsArray(j, i, numCols, numRows).astype(numpy.float)
# 
#    # do the calculations
#    mask = numpy.greater(data2 + data3, 0)
#    ndvi = numpy.choose(mask, (-99, (data3 - data2) / (data3 + data2)))
# 
#    # write the data
#    outBand.WriteArray(ndvi, j, i)
#===============================================================================

# read and write raster in memory
data2 = inBand2.ReadAsArray(0, 0, cols, rows).astype(numpy.float)
data3 = inBand3.ReadAsArray(0, 0, cols, rows).astype(numpy.float)

mask = numpy.greater(data2 + data3, 0)
ndvi = numpy.choose(mask, (-99, (data3 - data2) / (data3 + data2)))
outBand.WriteArray(ndvi, 0, 0)

# flush data to disk, set the NoData value and calculate stats
outBand.FlushCache()
outBand.SetNoDataValue(-99)
stats = outBand.GetStatistics(0, 1)

# georeference the image and set the projection
outDs.SetGeoTransform(inDs.GetGeoTransform())
outDs.SetProjection(inDs.GetProjection())

# build pyramids
gdal.SetConfigOption('HFA_USE_RRD', 'YES')
outDs.BuildOverviews(overviewlist=[2,4,8,16,32,64,128])

inDs = None
outDs = None