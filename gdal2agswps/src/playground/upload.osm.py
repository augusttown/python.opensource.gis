import os
from osgeo import ogr

rootDir = '/home/ying4682/Dropbox/Projects/osm.contribution/';
shpWorkspace = os.path.join(rootDir, 'shp', 'rancho.cucamonga.grided');
osmWorkspace = os.path.join(rootDir, 'osm', 'rancho.cucamonga.grided');

osmChangeWorkspace = os.path.join(rootDir, 'osm.changeset', 'rancho.cucamonga.grided');

shpDatasource = 'parcel_4326_grid_3_3_0_1.shp';
osmDatasource = 'parcel_4326_grid_3_3_0_1.osm'

def getExtent(shpDatasource):
    extent = [];
    return extent;

def polyshp2osm(shpDatasource):
    print('');



def osmosis(extent, osmDatasource):
    readApiCmd = 'osmosis --read-api ' + 'left=' + str(extent[0]) + ' ' + 'right=' + str(extent[2]) + ' ' + 'bottom=' + str(extent[1]) + ' ' + 'top=' + str(extent[3]) + ' '    
        
    print('');

if __name__ == '__main__':
    print('');
    
    
