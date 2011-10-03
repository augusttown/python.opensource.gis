import os
import sys
from osgeo import ogr
#
inputWorkspace = '/home/ying4682/Dropbox/Projects/osm.contribution/shp/rancho.cucamonga.grided/';
#
#inputDataPath = 'parcel_4326_1m_simplified_ags.shp';
inputDataPath = 'parcel_4326_grid_3_3_0_1.shp';
#
if __name__ == '__main__':
    #
    os.chdir(inputWorkspace);
    #    
    # load input shapefile
    inputDriver = ogr.GetDriverByName('ESRI Shapefile');
    inputDataSource = inputDriver.Open(inputDataPath, 0);
    # there is only one layer for shapefile datasource, so always get the first layer
    featureType = inputDataSource.GetLayer(0);
    extent = featureType.GetExtent();
     
    minx = extent[0];
    miny = extent[2];
    maxx = extent[1];
    maxy = extent[3];
    print(extent);
    sys.exit(1);
    # 6x8 grid
    numOfRow = 3;
    numOfCol = 3;
    
    if (minx > maxx) or (miny > maxy):
        print('invalid minx, miny, maxx, maxy values');
        sys.exit(1);
    else:
        dx = (maxx-minx)/numOfCol;
        dy = (maxy-miny)/numOfRow;
    
    y = miny;
    for rowIdx in range(numOfRow):       
        x = minx;
        for colIdx in range(numOfCol):
            print("extract features within extent: %5f,%5f,%5f,%5f"%(x, x+dx, y, y+dy));
            spat = str(x) + ' ' + str(y) + ' ' + str(x+dx)  + ' ' + str(y+dy);
            outputShpName = inputDataPath.split('.')[0] + '_' + str(rowIdx) + '_' + str(colIdx) + '.shp';
            outputShpPath = '../rancho.cucamonga.grided/' + outputShpName;
            ogr2ogrCmd = "ogr2ogr -f 'ESRI Shapefile' " + "-spat " + spat + " " + outputShpPath + " " + inputDataPath;
            print(ogr2ogrCmd);     
            os.system(ogr2ogrCmd);
            x = x + dx;
        y = y + dy;    
    