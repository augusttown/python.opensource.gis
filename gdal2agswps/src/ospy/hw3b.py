# import modules
import glob, os
#import hw3b_mod
from ospy import hw3b_mod 

# set the working directory
os.chdir(r'E:\documents\projects\ospy.2009\ospy_data3')

# loop through the shapefiles in the working directory
for inFN in glob.glob('*.shp'):
    # make the output filename
    outFN = inFN.replace('.shp', '_proj.shp')
    # reproject the shapefile
    hw3b_mod.reproject(inFN, 26912, outFN, 4269)
