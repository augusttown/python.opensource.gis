# high-pass filter using slice notation
import os, sys, time 
import numpy
from osgeo import gdal
from osgeo.gdalconst import GA_ReadOnly
from osgeo.gdalconst import GDT_Float32
# set start time
start = time.time()
# set home directory
os.chdir(r'E:\documents\projects\ospy.2009')
# register all of the GDAL drivers
gdal.AllRegister()
# open the image
inDs = gdal.Open(r'ospy_data6\aster.img', GA_ReadOnly)
if inDs is None:
    print 'Could not open aster.img'
    sys.exit(1)
# get image size
rows = inDs.RasterYSize
cols = inDs.RasterXSize

# read the input data
inBand = inDs.GetRasterBand(1)
inData = inBand.ReadAsArray(0, 0, cols, rows).astype(numpy.int)

# do the calculation
# calculate based on high-pass filter and slice notation
outData = numpy.zeros((rows, cols), numpy.float)
outData[1:rows-1,1:cols-1] = ((-0.7 * inData[0:rows-2,0:cols-2]) +
  (-1.0 * inData[0:rows-2,1:cols-1]) + (-0.7 * inData[0:rows-2,2:cols]) +
  (-1.0 * inData[1:rows-1,0:cols-2]) + (6.8 * inData[1:rows-1,1:cols-1]) +
  (-1.0 * inData[1:rows-1,2:cols]) + (-0.7 * inData[2:rows,0:cols-2]) +
  (-1.0 * inData[2:rows,1:cols-1]) + (-0.7 * inData[2:rows,2:cols]))

# create the output image
driver = inDs.GetDriver()
outDs = driver.Create(r'ospy_data6\aster_highpass.img', cols, rows, 1, GDT_Float32)
if outDs is None:
    print 'Could not create aster_highpass.img'
    sys.exit(1)
outBand = outDs.GetRasterBand(1)

# write the output data
outBand.WriteArray(outData, 0, 0)

# flush data to disk, set the NoData value and calculate stats
outBand.FlushCache()
stats = outBand.GetStatistics(0, 1)

# georeference the image and set the projection
outDs.SetGeoTransform(inDs.GetGeoTransform())
outDs.SetProjection(inDs.GetProjection())

inDs = None
outDs = None

print time.time() - start, 'seconds'