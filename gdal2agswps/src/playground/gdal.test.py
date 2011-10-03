# import system modules
import os
import sys
import math
# import numpy modules
import numpy
# import gdal related modules
from osgeo import ogr
from osgeo import osr
from osgeo import gdal
from osgeo.gdalconst import *
#from osgeo.gdalconst import GA_ReadOnly
#from osgeo.gdalconst import GF_Read    

# global variables
global DRIVERTYPE_TO_SUFFIX; 
DRIVERTYPE_TO_SUFFIX = {
    'GTiff':     '.tif',
    'BMP':       '.bmp',
    'AAIGrid':   '',   
    'ECW':       '.ecw',
    'EHdr':       '.bil',
    #'ENVI':       '.bil',
    #'ENVI':       '.bsq',
    'ENVI':       '.bip',  
    'GIF':          '.gif',
    'HDF4':         '.hdf',
    'HFA':          '.img',
    'INGR':         '.grd',
    'JPEG':         '.jpg',
    'JPEG2000':     '.jp2',
    'JP2KAK':       '.jp2',
    'KMLSUPEROVERLAY': '.kml',
    'NITF':         '.ntf',
    'NetCDF':       '.nc',
    'PNG':          '.png',
    'Rasterlite':   '.sqlite',
    'USGSDEM':      '.dem'
    # TODO: to add more
};

global PIXELDATATYPE_TO_PIXELDATATYPE;
PIXELDATATYPE_TO_PIXELDATATYPE = {
    'Byte': gdal.GDT_Byte,        # unsigned 8bit 
    'Float32': gdal.GDT_Float32,
    'Float64': gdal.GDT_Float64,
    'Int16': gdal.GDT_Int16,
    'Int32': gdal.GDT_Int32,
    'UInt16': gdal.GDT_UInt16,
    'UInt32': gdal.GDT_UInt32,
};

global GEOTIFF_CREATION_OPTS;
GEOTIFF_CREATION_OPTS = [];

global X_BLOCK_SIZE;
global Y_BLOCK_SIZE;
X_BLOCK_SIZE = 64;
Y_BLOCK_SIZE = 64;

# functions

if __name__ == '__main__':
    #
    # set current workspace
    #os.chdir(r'E:/data/dropbox/Dropbox/Projects/gdal2agswps.python/scratch/')
    os.chdir(r'E:/data/dropbox/Dropbox/Projects/gdal2agswps.python/data/');    
    
    # register all of the GDAL drivers
    gdal.AllRegister();
    print('register all gdal drivers');
    
    # input dataset path
    inputDatasetPath = 'imagine_3b_uint8.img';
    #inputDatasetPath = 'imagine_3b_uint8_4326.img';
    #inputDatasetPath = 'geotiff_3b_uint8.tif';
    #inputDatasetPath = 'geotiff_1b_uint8.tif';
    #inputDatasetPath = 'geotiff_1b_float32.tif';
    #inputDatasetPath = 'geotiff_1b_float32_4326.tif';
    # to consume WCS, open <WCS_GDAL> xml file see http://www.gdal.org/frmt_wcs.html
    #inputDatasetPath = 'wcs.gdal.xml';    
    # to consume WCS, open <WCS_GDAL> xml string see http://www.gdal.org/frmt_wcs.html
    #inputDatasetPath = '<WCS_GDAL><ServiceURL>http://char:6080/arcgis/services/haiti_3857/MapServer/WCSServer?</ServiceURL><CoverageName>1</CoverageName></WCS_GDAL>';
    #inputDatasetPath = 'wms.gdal.xml';
    
    print('input dataset path: %s'%inputDatasetPath);
    
    
    
    # output raster driver 
    # tiff/bigtiff/geotiff(.tif)
    #     http://www.gdal.org/frmt_gtiff.html    
    #outputDriverType = 'GTiff';            
    # Microsoft Windows Device Independent Bitmap (.bmp), gdal.GDT_Byte only
    # 
    #outputDriverType = 'BMP';              
    # AAIGrid -- Arc/Info ASCII Grid, gdal.GDT_Int32, supports only 1 band
    #outputDriverType = 'AAIGrid';          
    # ERDAS Compressed Wavelets (.ecw), only supports 8 bits per channel, need ECW SDK
    #     TODO: how to install ecw sdk
    #     http://www.gdal.org/frmt_ecw.html
    #outputDriverType = 'ECW';               
    # ESRI .hdr Labelled, ESRI BIL
    #     http://www.gdal.org/frmt_various.html#EHdr
    outputDriverType = 'EHdr';
    # ENVI .hdr Labelled Raster
    #     http://www.gdal.org/frmt_various.html#ENVI
    #outputDriverType = 'ENVI';   
    # Graphics Interchange Format (.gif)
    #     http://www.gdal.org/frmt_gif.html
    #outputDriverType = 'GIF'; 
    # Hierarchical Data Format Release 4 (HDF4), it doesn't seem to support Create() or CreateCopy()
    #     http://www.gdal.org/frmt_hdf4.html
    #outputDriverType = 'HDF4';
    # Erdas Imagine (.img)
    #     http://www.gdal.org/frmt_hfa.html
    #outputDriverType = 'HFA';
    # Intergraph Raster
    #     http://www.gdal.org/frmt_intergraphraster.html
    #outputDriverType = 'INGR';
    # JPEG JFIF (.jpg)
    #     http://www.gdal.org/frmt_jpeg.html
    #outputDriverType = 'JPEG';
    # JPEG2000 (.jp2, .j2k)
    #     http://www.gdal.org/frmt_jpeg2000.html
    #outputDriverType = 'JPEG2000';
    # KMLSUPEROVERLAY
    # 
    #outputDriverType = 'KMLSUPEROVERLAY';
    # NITF
    #     http://www.gdal.org/frmt_nitf.html
    #outputDriverType = 'NITF';        
    #outputCreateOpts = ['ICORDS=G'];        
    # NetCDF
    #     http://www.gdal.org/frmt_netcdf.html
    #outputDriverType = 'NetCDF';
    # PNG
    #     http://www.gdal.org/frmt_various.html#PNG
    #outputDriverType = 'PNG';
    #outputCreateOpts = ['WORLDFILE=YES'];
    # Rasterlite - Rasters in SQLite DB, OGR SQLite driver must have Spatialite support
    #     http://www.gdal.org/frmt_rasterlite.html
    #outputDriverType = 'Rasterlite';
    # USGS ASCII DEM / CDED (.dem)
    #     http://www.gdal.org/frmt_usgsdem.html
    #outputDriverType = 'USGSDEM';
    
    print('output dataset type: %s'%outputDriverType);
    
    #output dataset pixel data type
    #outputPixelDataTypeName = '';
    #outputPixelDataTypeName = 'Byte';
    outputPixelDataTypeName = 'Int16';
    #outputPixelDataTypeName = 'Int32';
    #outputPixelDataTypeName = 'Float32';
    outputPixelDataType = PIXELDATATYPE_TO_PIXELDATATYPE[outputPixelDataTypeName];
    
    # creation option    
    # creation options for Create() or CreateCopy()
    #     may overwrite options for a specific format 
    outputCreateOpts = [];
    
    # output dataset path
    outputDatasetName = 'output' + DRIVERTYPE_TO_SUFFIX[outputDriverType];
    # join and creat the output dataset path
    outputDatasetPath = os.path.join(os.path.pardir, 'scratch', outputDatasetName);
    #outputDatasetPath = "../scratch/output" + DRIVERTYPE_TO_SUFFIX[outputDriverType];
    print('output dataset path: %s'%outputDatasetPath);
    
    # output geotiff dataset path
    outputGeoTiffDatasetName = 'outputGeoTiff' + DRIVERTYPE_TO_SUFFIX['GTiff'];
    # join and creat the output geotiff dataset path
    outputGeoTiffDatasetPath = os.path.join(os.path.pardir, 'scratch', outputGeoTiffDatasetName);
    #outputGeoTiffDatasetPath = "../scratch/outputGeoTiff" + DRIVERTYPE_TO_SUFFIX['GTiff'];
    print('output geotiff dataset path: %s'%outputGeoTiffDatasetPath);
    
    # open input dataset in gdal
    # TODO: you don't need to specify the driver type, it seems to be able to recognize by itself
    inputDataset = gdal.Open(inputDatasetPath, GA_ReadOnly);
    if inputDataset is None:
        print('could not open %s'%inputDatasetPath);
        sys.exit(1);
        
    # gdal.Driver doesn't have a GetName(), use GetDescription()
    print('gdal driver name: ' + inputDataset.GetDriver().GetDescription());    
    # raster projection, GetProjection() return a wkt string 
    print('input dataset projection: ' + inputDataset.GetProjection());
    
    # import wkt string
    # input dataset crs as a wkt
    inputDatasetCrsWkt = inputDataset.GetProjection();
    # create input dataset crs
    inputDatasetCrs = osr.SpatialReference();
    inputDatasetCrs.ImportFromWkt(inputDatasetCrsWkt);
    
    # information about the raster
    inputDatasetRows = inputDataset.RasterYSize;
    inputDatasetCols = inputDataset.RasterXSize; 
    inputDatasetBandsCount = inputDataset.RasterCount;
    
    print('input dataset rows: ' + str(inputDatasetRows));
    print('input dataset cols: ' + str(inputDatasetCols));
    print('input dataset bands count: ' + str(inputDatasetBandsCount));
    
    # GetGeoTransformation of a raster dataset
    #     see http://www.gdal.org/gdal_tutorial.html   
    # adfGeoTransform[0] /* top left x */
    # adfGeoTransform[1] /* w-e pixel resolution */
    # adfGeoTransform[2] /* rotation, 0 if image is "north up" */
    # adfGeoTransform[3] /* top left y */
    # adfGeoTransform[4] /* rotation, 0 if image is "north up" */
    # adfGeoTransform[5] /* n-s pixel resolution */
    
    inputDatasetGeoTransform = inputDataset.GetGeoTransform();

    inputDatasetXOrigin = inputDatasetGeoTransform[0];
    inputDatasetYOrigin = inputDatasetGeoTransform[3];
    inputDatasetPixelResWE = inputDatasetGeoTransform[1];
    inputDatasetPixelResNS = inputDatasetGeoTransform[5];
    inputDatasetXRotation = inputDatasetGeoTransform[2];
    inputDatasetYRotation = inputDatasetGeoTransform[4];
    
    print('inputDataset origin: %s, %s'%(str(inputDatasetXOrigin),str(inputDatasetYOrigin)));
    print('inputDataset pixel resolution: %s, %s'%(str(inputDatasetPixelResWE),str(inputDatasetPixelResNS)));
    print('inputDataset rotation: %s, %s'%(str(inputDatasetXRotation),str(inputDatasetYRotation)));
    
    for bandIdx in range(inputDatasetBandsCount):
        # raster band index is '1' index based, not '0' index based
        inputDatasetBand = inputDataset.GetRasterBand(bandIdx+1);
        inputDatasetBandMin = inputDatasetBand.GetMinimum();
        inputDatasetBandMax = inputDatasetBand.GetMaximum();
        if inputDatasetBandMin is None or inputDatasetBandMax is None:
            (inputDatasetBandMin,inputDatasetBandMax) = inputDatasetBand.ComputeRasterMinMax(1);
        print('min=%.3f, max=%.3f'%(inputDatasetBandMin, inputDatasetBandMax));
    
        # raster band overview
        inputDatasetBandOverviewCount = inputDatasetBand.GetOverviewCount();
        print('inputDataset band overview count: ' + str(inputDatasetBandOverviewCount));
        # raster band color map
        inputDatasetBandColorTable = inputDatasetBand.GetColorTable();
        if inputDatasetBandColorTable is not None:
            print('inputDataset band color table count: ' + str(inputDatasetBandColorTable.GetCount()));
        else:
            print('inputDataset band does not have a color table');
         
        # read raster data   
        # read entire raster with ReadAsArray, which returns n-dimension (2d) array         
        #rasterData = inputDatasetBand.ReadAsArray(0, 0, inputDatasetCols, inputDatasetRows);
        # print out the central pixel value
        #rasterDataStr = str(rasterData[math.floor(inputDatasetCols/2), math.floor(inputDatasetRows/2)]);
        
        # read entire raster with ReadRaster, which returns one dimension bytes array
        #rasterData = inputDatasetBand.ReadRaster(0, 0, inputDatasetCols, inputDatasetRows);        
        # TODO: is there a low level function Band.RasterIO for reading raster?        
        # TODO: print out central pixel
                
        # read only a subset of raster, in this particular case, only one pixel
        #rasterData = inputDatasetBand.ReadAsArray(math.floor(inputDatasetCols/2), math.floor(inputDatasetRows/2), 1, 1);
        #print('pixel (%s,%s) value: %s'%(str(math.floor(inputDatasetCols/2)),str(math.floor(inputDatasetRows/2)),rasterDataStr));
            
    # gdal driver
    outputDriver = gdal.GetDriverByName(outputDriverType);
    if outputDriver is None:
        print('output driver type %s is invalid or not supported'%outputDriverType);
        sys.exit(1);
        
    # gdal driver metadata
    outputDriverMetadata = outputDriver.GetMetadata();    
    print('driver metadata');
    for medataKey in outputDriverMetadata:
        print('%s Driver Metadata %s: %s'%(outputDriverType, medataKey, outputDriverMetadata[medataKey]));
    
    # gdal driver to output GeoTiff
    outputGeoTiffDriver = gdal.GetDriverByName('GTiff');
    if outputGeoTiffDriver is None:
        print('output driver type GTiff is invalid or not supported');
        sys.exit(1);
    
    # geotiff gdal driver metadata
    outputGeoTiffDriverMetadata = outputGeoTiffDriver.GetMetadata();
    print('geotiff driver metadata');
    # print geotiff driver metadata items
    for geotiffMedataKey in outputGeoTiffDriverMetadata:
        print('GeoTiff Driver Metadata %s: %s'%(geotiffMedataKey, outputGeoTiffDriverMetadata[geotiffMedataKey]));

    # convert to output format
    if(gdal.DCAP_CREATE in outputDriverMetadata) and (outputDriverMetadata[gdal.DCAP_CREATE]=='YES'):        
        #
        print('output driver %s supports Create() method.'%outputDriverType);
        # copy input dataset to output dataset manually
        # create output dataset
        # TODO: specify output dataset pixel type
        print('create output dataset using Create() function.');
        outputDataset = outputDriver.Create(outputDatasetPath, inputDatasetCols, inputDatasetRows, inputDatasetBandsCount, outputPixelDataType, outputCreateOpts);
        # set output dataset GeoTransformation
        outputDataset.SetGeoTransform(inputDatasetGeoTransform);
        # set output dataset coordinate reference system
        outputDataset.SetProjection(inputDatasetCrsWkt);
        # check if output raster creation is successful
        if outputDataset is None:
            print('could not create output dataset: %s'%outputDatasetPath);        
        for bandIdx in range(inputDatasetBandsCount):
            outputDatasetBand = outputDataset.GetRasterBand(bandIdx+1);
            inputDatasetBand = inputDataset.GetRasterBand(bandIdx+1);
            for i in range(0, inputDatasetRows, Y_BLOCK_SIZE):
                if i + Y_BLOCK_SIZE < inputDatasetRows:
                    numRows = Y_BLOCK_SIZE;
                else:
                    numRows = inputDatasetRows - i;
                # loop through the columns
                for j in range(0, inputDatasetCols, X_BLOCK_SIZE):
                    if j + X_BLOCK_SIZE < inputDatasetCols:
                        numCols = X_BLOCK_SIZE;
                    else:                    
                        numCols = inputDatasetCols - j;        
                    # read the data in
                    # what numpy float format
                    inputRasterDataBlock = inputDatasetBand.ReadAsArray(j, i, numCols, numRows).astype(numpy.float);            
                    # do any calculation or donation here
                    # TODO:
                    #print('write block index: [%s,%s]'%(str(i),str(j)));
                    #print('write block size: [%s,%s]'%(str(numRows),str(numCols)));
                    outputDatasetBand.WriteArray(inputRasterDataBlock, j, i);
    elif(gdal.DCAP_CREATECOPY in outputDriverMetadata) and outputDriverMetadata[gdal.DCAP_CREATECOPY]=='YES':        
        print('output driver %s supports CreateCopy() method.'%outputDriverType);            
        # copy input dataset to output dataset
        # Driver.CreateCopy()
        #     
        # raster dataset format creation options can be passed in as "key=value" in the last array parameter
        print('create output dataset using CreateCopy() function.');
        outputDataset = outputDriver.CreateCopy(outputDatasetPath, inputDataset, 0, outputCreateOpts);
        #        
    else:
        print('driver type %s does not support either create() or createCopy() features'%outputDriverType);
        print('skip converting');
    
    # convert to geotiff output format 
    if(gdal.DCAP_CREATECOPY in outputGeoTiffDriverMetadata) and outputGeoTiffDriverMetadata[gdal.DCAP_CREATECOPY]=='YES':  
        print('output driver GTiff supports CreateCopy() method.');
        print('create output GeoTiff using CreateCopy() function.');
        outputGeoTiffDataset = outputGeoTiffDriver.CreateCopy(outputGeoTiffDatasetPath, inputDataset, 0, GEOTIFF_CREATION_OPTS);
    
    # TODO: is this the correct way to destory/release memory of input dataset
    inputDataset = None;
    outputDataset = None;
    outputGeoTiffDataset = None;
    