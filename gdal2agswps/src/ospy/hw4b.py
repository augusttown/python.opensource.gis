# import system modules
import os, sys
# import local modules
import hw4b_util
# import gdal modules and numpy module
use_numeric = True
try:
    from osgeo import ogr
    from osgeo import gdal
    from osgeo.gdalconst import *
    import numpy
    os.chdir(r'E:\documents\projects\ospy.2009')
    use_numeric = False
except ImportError:
    import ogr, gdal
    from gdalconst import *
    import Numeric
    os.chdir(r'E:\documents\projects\ospy.2009')

# register all of the GDAL drivers
gdal.AllRegister()

# open the image
ds = gdal.Open(r'ospy_data4\aster.img', GA_ReadOnly)
if ds is None:
    print 'Could not open aster.img'
    sys.exit(1)

# get image size
rows = ds.RasterYSize
cols = ds.RasterXSize
bands = ds.RasterCount

print 'rows: ' + str(rows)
print 'cols: ' + str(cols)
print 'bands: ' + str(bands)

# get the band and block sizes
band = ds.GetRasterBand(1)
# read entire image

#==============================================================================
# all_data = band.ReadAsArray(0, 0, cols, rows)
# for i in range(rows):
#   for j in range(cols):
#       value = all_data[i,j]
#       if value > 0:
#           print all_data[i,j]
#==============================================================================

# GetBlockSize() in util doesn't work
#blockSizes = hw4b_util.GetBlockSize(band)
#xBlockSize = blockSizes[0]
#yBlockSize = blockSizes[1]

# ERDAS .img file default block size is 64 pixels
xBlockSize = 64
yBlockSize = 64

# initialize variables
count = 0
total = 0

# loop through the rows
for i in range(0, rows, yBlockSize):
    if i + yBlockSize < rows:
        numRows = yBlockSize
    else:
        numRows = rows - i

    # loop through the columns
    for j in range(0, cols, xBlockSize):
        if j + xBlockSize < cols:
            numCols = xBlockSize
        else:
            numCols = cols - j

        # read the data and do the calculations
        if use_numeric: # use Numberic
            # ReadAsArray always crash on Windows 7
            data = band.ReadAsArray(j, i, numCols, numRows).astype(Numeric.Float)
            mask = Numeric.greater(data, 0)
            count = count + Numeric.sum(Numeric.sum(mask))
            total = total + Numeric.sum(Numeric.sum(data))
        else:           # use numpy
            # ReadAsArray always crash on Windows 7
            data = band.ReadAsArray(j, i, numCols, numRows).astype(numpy.float)
            print 'read: ' + str(j) + "," + str(i) + "," + str(numCols) + "," + str(numRows) 
            mask = numpy.greater(data, 0)
            count = count + numpy.sum(numpy.sum(mask))
            total = total + numpy.sum(numpy.sum(data))

# print results
print 'Ignoring 0:', total/count
print 'Including 0:', total/(rows*cols)