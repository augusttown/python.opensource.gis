# import system modules
import os;
import sys;
import math;
# import numpy modules
import numpy;
# import gdal related modules
from osgeo import ogr;
from osgeo import osr;
from osgeo import gdal;
from osgeo.gdalconst import *;
# import arcpy modules
#import arcpy;
#
#arcpy.AddMessage('');
#print('');

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

# functions
def ags_wps_gdal_translate(inputDatasetPath, outputDriverType, outputPixelDataTypeName, outputCreationOpts, outputGeoTiffCreationOpts):
    #
    # output dataset path
    outputDatasetName = 'output' + DRIVERTYPE_TO_SUFFIX[outputDriverType];
    # join and creat the output dataset path
    outputDatasetPath = os.path.join(os.path.pardir, 'scratch', outputDatasetName);
    #outputDatasetPath = os.path.join(arcpy.env.scratchWorkspace, outputDatasetName);
    print('output dataset path: %s'%outputDatasetPath);
    #arcpy.AddMessage('output dataset path: %s'%outputDatasetPath);
    
    # output geotiff dataset path
    outputGeoTiffDatasetName = 'outputGeoTiff' + DRIVERTYPE_TO_SUFFIX['GTiff'];
    # join and creat the output geotiff dataset path
    outputGeoTiffDatasetPath = os.path.join(os.path.pardir, 'scratch', outputGeoTiffDatasetName);
    #outputGeoTiffDatasetPath = os.path.join(arcpy.env.scratchWorkspace, outputGeoTiffDatasetName);
    print('output geotiff dataset path: %s'%outputGeoTiffDatasetPath);
    #arcpy.AddMessage('output geotiff dataset path: %s'%outputGeoTiffDatasetPath);
    
    # open input dataset in gdal
    # TODO: you don't need to specify the driver type, it seems to be able to recognize by itself
    inputDataset = gdal.Open(inputDatasetPath, GA_ReadOnly);
    if inputDataset is None:
        print('could not open %s'%inputDatasetPath);
        #arcpy.AddMessage('could not open %s'%inputDatasetPath);
        sys.exit(1);
        
    # gdal.Driver doesn't have a GetName(), use GetDescription()
    print('gdal driver name: %s'%inputDataset.GetDriver().GetDescription());
    #arcpy.AddMessage('gdal driver name: %s'%inputDataset.GetDriver().GetDescription());    
    # raster projection, GetProjection() return a wkt string 
    print('input dataset projection: %s'%inputDataset.GetProjection());
    #arcpy.AddMessage('input dataset projection: %s'%inputDataset.GetProjection());
           
    # gdal driver
    outputDriver = gdal.GetDriverByName(outputDriverType);
    if outputDriver is None:
        print('output driver type %s is invalid or not supported'%outputDriverType);
        #arcpy.AddMessage('output driver type %s is invalid or not supported'%outputDriverType);
        sys.exit(1);
    
    # gdal driver metadata
    outputDriverMetadata = outputDriver.GetMetadata();    
    #print('driver metadata');
    ##arcpy.AddMessage('driver metadata');
    #for medataKey in outputDriverMetadata:
    #    print('%s Driver Metadata %s: %s'%(outputDriverType, medataKey, outputDriverMetadata[medataKey]));
    #    #arcpy.AddMessage('%s Driver Metadata %s: %s'%(outputDriverType, medataKey, outputDriverMetadata[medataKey]));
    
    # gdal driver to output GeoTiff
    outputGeoTiffDriver = gdal.GetDriverByName('GTiff');
    if outputGeoTiffDriver is None:
        print('output driver type GTiff is invalid or not supported');
        #arcpy.AddMessage('output driver type GTiff is invalid or not supported');
        sys.exit(1);
    
    # geotiff gdal driver metadata
    outputGeoTiffDriverMetadata = outputGeoTiffDriver.GetMetadata();
    #print('geotiff driver metadata');
    ##arcpy.AddMessage('geotiff driver metadata');
    # print geotiff driver metadata items
    #for geotiffMedataKey in outputGeoTiffDriverMetadata:
    #    print('GeoTiff Driver Metadata %s: %s'%(geotiffMedataKey, outputGeoTiffDriverMetadata[geotiffMedataKey]));
    #    #arcpy.AddMessage('GeoTiff Driver Metadata %s: %s'%(geotiffMedataKey, outputGeoTiffDriverMetadata[geotiffMedataKey]));
    
    if(gdal.DCAP_CREATECOPY in outputDriverMetadata) and outputDriverMetadata[gdal.DCAP_CREATECOPY]=='YES':        
        print('output driver %s supports CreateCopy() method.'%outputDriverType);       
        #arcpy.AddMessage('output driver %s supports CreateCopy() method.'%outputDriverType);            
        # copy input dataset to output dataset
        # Driver.CreateCopy()
        #     
        # raster dataset format creation options can be passed in as "key=value" in the last array parameter
        print('create output dataset using CreateCopy() function.');
        #arcpy.AddMessage('create output dataset using CreateCopy() function.');
        #outputDataset = outputDriver.CreateCopy(outputDatasetPath, inputDataset, 0, outputCreationOpts);
        outputDataset = outputDriver.CreateCopy(str(outputDatasetPath), inputDataset, 0, []);
        #        
    else:
        print('driver type %s does not support createCopy() features'%outputDriverType);
        #arcpy.AddMessage('driver type %s does not support createCopy() features'%outputDriverType);
        print('skip converting');
        #arcpy.AddMessage('skip converting');
    
    # convert to geotiff output format 
    if(gdal.DCAP_CREATECOPY in outputGeoTiffDriverMetadata) and outputGeoTiffDriverMetadata[gdal.DCAP_CREATECOPY]=='YES':  
        print('output driver GTiff supports CreateCopy() method.');
        #arcpy.AddMessage('output driver GTiff supports CreateCopy() method.');
        print('create output GeoTiff using CreateCopy() function.');
        #arcpy.AddMessage('create output GeoTiff using CreateCopy() function.');
        #outputGeoTiffDataset = outputGeoTiffDriver.CreateCopy(outputGeoTiffDatasetPath, inputDataset, 0, outputGeoTiffCreationOpts);
        outputGeoTiffDataset = outputGeoTiffDriver.CreateCopy(str(outputGeoTiffDatasetPath), inputDataset, 0, []);
    else:
        print('driver type GTiff does not support createCopy() features');
        #arcpy.AddMessage('driver type GTiff does not support createCopy() features');
        print('skip converting to GeoTiff');
        #arcpy.AddMessage('skip converting to GeoTiff');
        
    # TODO: is this the correct way to destory/release memory of input dataset
    print('release input and output dataset resource');
    #arcpy.AddMessage('release input and output dataset resource');
    inputDataset = None;
    outputDataset = None;
    outputGeoTiffDataset = None;
    
    print('return output dataset and GeoTiff path');
    #arcpy.AddMessage('return output dataset and GeoTiff path');
    return [outputDatasetPath, outputGeoTiffDatasetPath];

if __name__ == '__main__':
    #
    # print out system environment variables    
    sorted(os.environ);
    #print(os.environ);
    #arcpy.AddMessage(os.environ);
    
    
    # set current workspace
    #os.chdir(r'E:/data/dropbox/Dropbox/Projects/gdal2agswps.python/scratch/');
    os.chdir(r'E:/data/dropbox/Dropbox/Projects/gdal2agswps.python/data/');    
    print('os.curdir: ' + os.curdir);
    #arcpy.AddMessage('os.curdir: ' + os.curdir);
    
    
    #arcpyScratchWorkspaceFgdbPath = os.path.join(arcpy.env.scratchWorkspace, 'scratch.gdb');
    #print('arcpyScratchWorkspaceFgdbPath: %s'%arcpyScratchWorkspaceFgdbPath);    
    #arcpy.AddMessage('arcpyScratchWorkspaceFgdbPath: %s'%arcpyScratchWorkspaceFgdbPath);
    #arcpy.env.overwriteOutput = True
    ##arcpy.AddMessage(arcpy.env.overwriteOutput);
    
    # register all of the GDAL drivers
    gdal.AllRegister();
    #arcpy.AddMessage('register all gdal drivers');
    print('register all gdal drivers');
    
    # gdal.driver.ags python script tool parameters list
    # input parameters:
    #     inputDatasetPath - 0
    #     outputDriverType - 1
    #     outputPixelDataTypeName - 2
    #     outputCreationOpts - 3
    #     outputGeoTiffCreationOpts - 4
    # output parameters:
    #     outputDatasetPath - 5
    #     outputGeoTiffDatasetPath - 6
    
    # input dataset path
    #inputDatasetPath = 'imagine_3b_uint8.img';
    #inputDatasetPath = 'imagine_3b_uint8_4326.img';
    #inputDatasetPath = 'geotiff_3b_uint8.tif';
    #inputDatasetPath = 'http://august-resources.appspot.com/sample.data/geotiff_3b_uint8.tif'
    #inputDatasetPath = 'geotiff_1b_uint8.tif';
    #inputDatasetPath = 'geotiff_1b_float32.tif';
    #inputDatasetPath = 'geotiff_1b_float32_4326.tif';
    # to consume WCS, open <WCS_GDAL> xml file see http://www.gdal.org/frmt_wcs.html
    #inputDatasetPath = 'wcs.gdal.xml';    
    # to consume WCS, open <WCS_GDAL> xml string see http://www.gdal.org/frmt_wcs.html
    inputDatasetPath = '<WCS_GDAL><ServiceURL>http://char:6080/arcgis/services/haiti_3857/MapServer/WCSServer?</ServiceURL><CoverageName>1</CoverageName></WCS_GDAL>';
    #inputDatasetPath = 'wms.gdal.xml';
    
    #take input dataset path from user input
    #inputDatasetPath = arcpy.GetParameterAsText(0);    
    print('input dataset path: %s'%inputDatasetPath);
    #arcpy.AddMessage('input dataset path: %s'%inputDatasetPath);
    
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
    #
    # take outputDriverType from user input
    #outputDriverType = arcpy.GetParameterAsText(1);
    print('output dataset type: %s'%outputDriverType);
    #arcpy.AddMessage('output dataset type: %s'%outputDriverType);
    
    #output dataset pixel data type
    #outputPixelDataTypeName = '';
    #outputPixelDataTypeName = 'Byte';
    outputPixelDataTypeName = 'Int16';
    #outputPixelDataTypeName = 'Int32';
    #outputPixelDataTypeName = 'Float32';
    outputPixelDataType = PIXELDATATYPE_TO_PIXELDATATYPE[outputPixelDataTypeName];
    # take outputPixelDataTypeName from user input
    #outputPixelDataTypeName = arcpy.GetParameterAsText(2);
    print('output dataset pixel datatype: %s'%outputPixelDataType);
    #arcpy.AddMessage('output dataset pixel datatype: %s'%outputPixelDataType);
    
    # creation option    
    # creation options for Create() or CreateCopy()
    #     may overwrite options for a specific format 
    outputCreationOpts = [];
    # take outputCreationOpts from user input
    #outputCreationOpts = arcpy.GetParameterAsText(3);
    print('output dataset creation options: %s'%outputCreationOpts);
    #arcpy.AddMessage('output dataset creation options: %s'%outputCreationOpts);
    
    # geotiff creation options
    # creation options for Create() or CreateCopy()
    outputGeoTiffCreationOpts = GEOTIFF_CREATION_OPTS;
    # take outputGeoTiffCreationOpts from user input
    #outputGeoTiffCreationOpts = arcpy.GetParameterAsText(4);
    print('output GeoTiff creation options: %s'%outputGeoTiffCreationOpts);
    #arcpy.AddMessage('output GeoTiff creation options: %s'%outputGeoTiffCreationOpts);
    #
    # call function ags_wps_gdal_translate
    print('call function ags_wps_gdal_translate');
    #arcpy.AddMessage('call function ags_wps_gdal_translate');
    outputPaths = ags_wps_gdal_translate(inputDatasetPath, outputDriverType, outputPixelDataTypeName, outputCreationOpts, outputGeoTiffCreationOpts);
    #
    outputDatasetPath = outputPaths[0];
    print('outputDatasetPath: %s'%outputDatasetPath);
    #arcpy.AddMessage('outputDatasetPath: %s'%outputDatasetPath);
    #arcpy.SetParameterAsText(5, str(outputDatasetPath));
    
    outputGeoTiffDatasetPath = outputPaths[1];
    print('outputGeoTiffDatasetPath: %s'%outputGeoTiffDatasetPath);
    #arcpy.AddMessage('outputGeoTiffDatasetPath: %s'%outputGeoTiffDatasetPath);
    #arcpy.SetParameterAsText(6, str(outputGeoTiffDatasetPath));

    