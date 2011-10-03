# high-pass filter using pixel notation
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
inDs = gdal.Open(r'ospy_data6\smallaster.img', GA_ReadOnly)
if inDs is None:
    print 'Could not open smallaster.img'
    sys.exit(1)

# get image size
rows = inDs.RasterYSize
cols = inDs.RasterXSize

# read the input data
inBand = inDs.GetRasterBand(1)
inData = inBand.ReadAsArray(0, 0, cols, rows).astype(numpy.float)

# do the calculation
outData = numpy.zeros((rows, cols), numpy.float)
for i in range(1, rows-1):
    for j in range(1, cols-1):
        outData[i,j] = ((-0.7 * inData[i-1,j-1]) + (-1.0 * inData[i-1,j]) + (-0.7 * inData[i-1,j+1]) +
            (-1.0 * inData[i,j-1]) + (6.8 * inData[i,j]) + (-1.0 * inData[i,j+1]) +
            (-0.7 * inData[i+1,j-1]) + (-1.0 * inData[i+1,j]) + (-0.7 * inData[i+1,j+1]))

# create the output image
driver = inDs.GetDriver()
outDs = driver.Create(r'ospy_data6\smallaster_highpass.img', cols, rows, 1, GDT_Float32)
if outDs is None:
    print 'Could not create smallaster_highpass.img'
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