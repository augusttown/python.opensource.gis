# import system modules
import os
import sys
import string
#
# import gdal/ogr modules
from osgeo import ogr
from osgeo import osr
# import arcpy modules
#import arcpy
#
###arcpy.AddMessage('');
#print('');

global driverTypeToFileSuffix; 
driverTypeToFileSuffix = {
    'ESRI Shapefile':     '.shp',
    'FileGDB':            '',
    'GPX':                '.gpx',
    'GeoRSS':             '.xml',
    'GeoJSON':            '.json',
    'SVG':                '.svg'
    # TODO: to add more
};
        
def ags_wps_ogr2ogr(inputDataPath, inputDriverType, inputFeatureTypeName, outputDriverType, outputDataSourceOpts):
    #arcpy.AddMessage('...ags_wps_ogr2ogr...');
    #print('call function ags_wps_ogr2ogr');
    
    # input ogr driver
    inputDriver = ogr.GetDriverByName(inputDriverType)
    #arcpy.AddMessage('ogr driver for input dataset: ' + inputDriverType);
    print('ogr driver for input dataset: ' + inputDriverType);
        
    # output ogr driver
    outputDriver = ogr.GetDriverByName(outputDriverType);
    #arcpy.AddMessage('ogr driver for output dataset: ' + outputDriverType);
    print('ogr driver for output dataset: ' + outputDriverType);

    # output shapefile driver
    # always output as shapefile
    outputShpDriver = ogr.GetDriverByName('ESRI Shapefile');       
    # output fgdb driver
    # always output as fgdb
    outputFgdbDriver = ogr.GetDriverByName('FileGDB');
    
    # open input data        
    inputDataSource = inputDriver.Open(inputDataPath, 0);                 
    #arcpy.AddMessage('open input data source: ' + inputDataPath);
    print('open input data source: ' + inputDataPath);
        
    # error handling
    if inputDataSource is None:
        #arcpy.AddMessage('could not open input data source');
        print('could not open input data source');
        sys.exit(1);
    
    # feature type count
    # for data source like WFS there can be more than 1 layer
    featureTypeCount = inputDataSource.GetLayerCount();
    #arcpy.AddMessage('feature type count:' + str(featureTypeCount));
    print('feature type count:' + str(featureTypeCount));
    
    if(inputFeatureTypeName!='') and (inputFeatureTypeName is not None):
        # look for feature type/layer by name
        featureType = inputDataSource.GetLayerByName(inputFeatureTypeName);
    else:
        # assume there is only one feature type/layer in the data source
        featureType = inputDataSource.GetLayer(0);
    
    # NOTE: instead of getting all the features from a feature type, call inputDataSource.ExecuteSQL()
    #     to get a feature type/layer with a subset of features
    #     http://gdal.org/python/osgeo.ogr.DataSource-class.html#ExecuteSQL
    #featureTypeWithSql = inputDataSource.ExecuteSQL("SELECT * FROM shapefile");    # select all features, same as GetLayerByName('shapefile');
    #featureTypeWithSql = inputDataSource.ExecuteSQL("SELECT * FROM shapefile WHERE TYPE = \"Gas\"");    # select only "Gas" point features from shapefile 
    #featureType = featureTypeWithSql;
    
    # NOTE: alternative code 
    # loop through all available feature types to find a match
    #===========================================================================
    # if featureTypeCount >= 0:
    #    for featureTypeIdx in range(featureTypeCount):
    #        # feature type
    #        print('featureTypeIdx: ' + str(featureTypeIdx))
    #        featureType = inputDataSource.GetLayer(featureTypeIdx)                 
    #        #
    #        try:
    #            print('feature type name: ' + featureType.GetName())
    #            #   
    #            if featureType is not None:
    #                print('found feature type: ' + featureType.GetName())
    #                featureTypeName = featureType.GetName()                                
    #                if (inputFeatureTypeName!='') and (featureTypeName!=inputFeatureTypeName):
    #                    print('skip mismatch feature type: ' + featureTypeName)
    #                    continue;      
    #        except ValueError:               
    #            print('error: skip input feature type: ' + featureType.GetName())       
    #===========================================================================
          
    if featureType is not None:        
        #arcpy.AddMessage('process feature type: ' + featureType.GetName());
        print('process feature type: ' + featureType.GetName());        
        try:
            # default spatial reference
            inputCrs = featureType.GetSpatialRef();
            #arcpy.AddMessage('input feature type spatial reference system: ' + str(inputCrs));
            print('input feature type spatial reference system: ' + str(inputCrs));
            # output spatial reference the same as input spatial reference
            # TODO: may take it from geo-processing environment                    
            if inputCrs is None:
                # some data source like csv may not carry spatial reference system information
                defaultCrs = osr.SpatialReference();
                #defaultCrs.ImportFromEPSG(4326);     # default to EPSG:4326
                defaultCrs.ImportFromEPSG(900913);    # default to EPSG:900913
                outputCrs = defaultCrs.Clone();
            else:
                outputCrs = inputCrs.Clone(); 
            
            #arcpy.AddMessage('output feature type spatial reference system: ' + str(outputCrs));
            print('output feature type spatial reference system: ' + str(outputCrs));                                            
                
            # how to obtain the dynamic scratchworkspace path when running as GP service in ArcGIS Server
            # when GP is in asynchronous mode, always build path relative to the scratchworkspace by using 
            #     os.path.join(arcpy.env.scratchWorkspace, 'subfolder1', 'subfolder2', ..., 'subfoldern');
            outputFeatureTypeName = 'output';
            #outputPath = os.path.join(arcpy.env.scratchWorkspace, (outputFeatureTypeName + driverTypeToFileSuffix[outputDriverType]));                                      
            outputPath = "../scratch/output" + driverTypeToFileSuffix[outputDriverType];            
                        
            # without giving .shp suffix, a folder will be created to contain the output shapefile
            # doing ArcGIS Server GP way, so other tools/modules can take this as input 
            outputShpFeatureTypeName = 'outputShpForAgs';
            #outputShpPath = os.path.join(arcpy.env.scratchWorkspace, (outputShpFeatureTypeName + driverTypeToFileSuffix['ESRI Shapefile']));
            outputShpPath = '../scratch/outputShpForAgs' + driverTypeToFileSuffix['ESRI Shapefile'];                                                                 
            
            outputFgdbFeatureTypeName = 'outputFgdbForAgs';
            #outputFgdbPath = os.path.join(arcpy.env.scratchWorkspace, 'scratch.gdb', (outputFgdbFeatureTypeName + driverTypeToFileSuffix['FileGDB']));
            outputFgdbPath = '../scratch/outputFgdbForAgs' + driverTypeToFileSuffix['FileGDB'];            
                        
            # remove existing user defined output
            if os.path.exists(outputPath):                                       # test if file already exists
                outputDriver.DeleteDataSource(outputPath);                       # if exists, delete it
                #arcpy.AddMessage('delete existing output data');
                print('delete existing output data');
            
            # remove existing shapefile output
            if os.path.exists(outputShpPath):                                    # test if file already exists
                outputShpDriver.DeleteDataSource(outputShpPath);                 # if exists, delete it
                #arcpy.AddMessage('delete existing output shapefile');
                print('delete existing output shapefile');
            
            # remove existing fgdb output
            if os.path.exists(outputFgdbPath):                                   # test if file already exists
                outputShpDriver.DeleteDataSource(outputFgdbPath);                # if exists, delete it
                #arcpy.AddMessage('delete existing output shapefile');
                print('delete existing output shapefile');
            
            # create output data source
            # ogr.Driver.CreateDataSource(GRSFDriverH hDriver, const char *pszName, char **papszOptions) 
            #     attempts to create a new data source based on the passed driver.
            #     the papszOptions argument can be used to control driver specific creation options. 
            #     these options are normally documented in the format specific documentation.
            #     it is important to call OGR_DS_Destroy() when the datasource is no longer used to ensure that all data has been properly flushed to disk.
        
            #   pszName:  the name for the new data source. UTF-8 encoded.
            #   papszOptions:  a StringList of name=value options. Options are driver
            #       specific, and driver information can be found at the following
            #       url:http://www.gdal.org/ogr/ogr_formats.html
                            
            #     outputPath is the path relative to os.curdir
            #     outputPath is where result shapefile will be generated
            # take data source creation                      
            if outputDataSourceOpts is None:
                dataSourceOpts = [];
            else:
                dataSourceOpts = outputDataSourceOpts;
            #
            outputDataSource = outputDriver.CreateDataSource(outputPath, dataSourceOpts);              
            if outputDataSource is None:
                #arcpy.AddMessage('could not create output data source');
                print('could not create output data source' + outputPath);
                sys.exit(1);
            #            
            #arcpy.AddMessage('create output data source: ' + outputPath);
            print('create output data source: ' + outputPath);
            
            outputShpDataSource = outputShpDriver.CreateDataSource(outputShpPath);              
            if outputShpDataSource is None:
                #arcpy.AddMessage('could not create output shapefile data source' + outputShpPath);
                print('could not create output shapefile data source' + outputShpPath);
                sys.exit(1)
            #
            #arcpy.AddMessage('create output data source: ' + outputShpPath);
            print('create output shapefile data source: ' + outputShpPath);
                                                
            # feature type feature definition
            featureTypeDef = featureType.GetLayerDefn();            
            # feature type geometry type definition     
            featureTypeGeomDef = featureTypeDef.GetGeomType();
            #arcpy.AddMessage('input feature type geometry: ' + str(featureTypeGeomDef));
            print('input feature type geometry: ' + str(featureTypeGeomDef));
            #arcpy.AddMessage('output feature type geometry: ' + str(featureTypeGeomDef));
            print('output feature type geometry: ' + str(featureTypeGeomDef));
                            
            # create output feature type
            outputFeatureType = outputDataSource.CreateLayer(outputFeatureTypeName, geom_type=featureTypeGeomDef);
            # create output shapefile feature type
            outputShpFeatureType = outputShpDataSource.CreateLayer(outputShpFeatureTypeName, geom_type=featureTypeGeomDef);
            
            # clone attribute fields
            #   the list of attribute fields includes the geometry field
            featureTypeFieldCount = featureTypeDef.GetFieldCount();
            for featureTypeFieldIdx in range(featureTypeFieldCount):
                featureTypeField = featureTypeDef.GetFieldDefn(featureTypeFieldIdx);
                # create output feature type field
                outputFeatureType.CreateField(featureTypeField);
                # create output shapefile feature type field
                outputShpFeatureType.CreateField(featureTypeField);
                #arcpy.AddMessage('create output feature type field: ' + str(featureTypeField.GetName()) + '[' + str(featureTypeField.GetType()) + ']');
                print('create output feature type field: ' + str(featureTypeField.GetName()) + '[' + str(featureTypeField.GetType()) + ']'); 
            # output feature type definition
            outputFeatureTypeDef = outputFeatureType.GetLayerDefn();
            # output shapefile feature type definition
            outputShpFeatureTypeDef = outputShpFeatureType.GetLayerDefn();
            
            # loop through each feature
            feature = featureType.GetNextFeature();
            
            while feature:
                outputFeature = ogr.Feature(outputFeatureTypeDef);
                outputShpFeature = ogr.Feature(outputShpFeatureTypeDef);
                
                # TODO: you may need to create geometry field manually from non-spatial fields
                #     e.g. CSV  
                outputFeatureGeom = feature.GetGeometryRef();
                outputShpFeatureGeom = feature.GetGeometryRef();
                
                # it seems that if the coordinate values are in scientific notation OGR has problem
                #x = str(outputFeatureGeom.GetX());
                #y = str(outputFeatureGeom.GetY());                    
                                           
                outputFeature.SetGeometry(outputFeatureGeom);
                outputShpFeature.SetGeometry(outputShpFeatureGeom);
                
                #arcpy.AddMessage('set output feature geometry type');
                print('set output feature geometry type'); 
                
                # loop through attributes for each feature 
                for featureTypeFieldIdx in range(featureTypeFieldCount):
                    outputFeature.SetField(featureTypeFieldIdx, feature.GetField(featureTypeFieldIdx));
                    outputShpFeature.SetField(featureTypeFieldIdx, feature.GetField(featureTypeFieldIdx));
                #arcpy.AddMessage('set output feature attributes')
                print('set output feature attributes');     
                
                # create a new feature
                outputFeatureType.CreateFeature(outputFeature);
                outputShpFeatureType.CreateFeature(outputShpFeature);
                #arcpy.AddMessage('create output feature');
                #print('create output feature');
                
                # destroy temporary features
                outputFeature.Destroy;
                outputShpFeature.Destroy;
                feature.Destroy;
                # loop to the next feature
                feature = featureType.GetNextFeature();                            
                                    
            # morph to be ESRI compatible
            outputCrs.MorphToESRI(); 
            #arcpy.AddMessage('convert projection wkt to esri format');
            print('convert projection wkt to esri format');       
            #arcpy.AddMessage(outputCrs);
            #print str(outputCrs);
            
            # write out .prj file                            
            # if it is shape file, generate .prj file                          
            if outputDriverType == 'ESRI Shapefile':                        
                outputFeatureTypePrjPath = outputPath.replace('.shp', '.prj');
                if os.path.exists(outputFeatureTypePrjPath):                                    # test if file already exists
                    # TODO: how to delete a file in python 
                    #arcpy.AddMessage('delete existing .prj file');
                    print('delete existing .prj file');                         
                # generate new .prj file
                outputFeatureTypePrj = open(outputFeatureTypePrjPath, 'w');
                outputFeatureTypePrj.write(outputCrs.ExportToWkt());
                outputFeatureTypePrj.close();
                #arcpy.AddMessage('create new .prj file');
                print('create new .prj file');
            
            # write out .prj file for shapefile output    
            outputShpFeatureTypePrjPath = outputShpPath.replace('.shp', '.prj');
            if os.path.exists(outputShpFeatureTypePrjPath):                                    # test if file already exists
                # TODO: how to delete a file in python 
                #arcpy.AddMessage('delete existing .prj file');
                print('delete existing .prj file')                         
            # generate new .prj file
            outputShpFeatureTypePrj = open(outputShpFeatureTypePrjPath, 'w');
            outputShpFeatureTypePrj.write(outputCrs.ExportToWkt());
            outputShpFeatureTypePrj.close();
            #arcpy.AddMessage('create new .prj file');
            print('create new .prj file')    
            # destroy output data source
            outputDataSource.Destroy();
            outputShpDataSource.Destroy(); 
    
            # copy output shapefile to fgdb
            #arcpy.AddMessage('call CopyFeatures_management gp tool');
            print('call CopyFeatures_management gp tool')
            # 
            #arcpy.CopyFeatures_management(outputShpPath, outputFgdbPath);
            # destroy input data source
            inputDataSource.Destroy();
            # return output paths
            return [outputPath, outputShpPath, outputFgdbPath];
                            
        except ValueError:
            # do nothing
            #arcpy.AddMessage('error: skip input feature type: ' + featureType.GetName());
            print('error: skip input feature type: ' + featureType.GetName());
            # destroy input data source
            inputDataSource.Destroy();
            sys.exit(1);
    
    
if __name__ == '__main__':
    
    # print out system environment variables    
    sorted(os.environ);
    #arcpy.AddMessage(os.environ);
    print(os.environ);
    
    # set current workspace
    #os.chdir(r'C:/yingqi/nightingale/projects/python.opensource.gis/src/github/python.opensource.gis/gdal2agswps/data/scratch/');
    os.chdir(r'C:/yingqi/nightingale/projects/python.opensource.gis/src/github/python.opensource.gis/gdal2agswps/data/');
    #os.chdir(r'/home/ying4682/Dropbox/Projects/gdal2agswps.python/data/');    
    #os.chdir(r'/home/ying4682/Dropbox/Projects/osm.contribution/shp/rancho.cucamonga/');
    
    ##arcpy.AddMessage('os.curdir: ' + os.curdir);
    #print('os.curdir: ' + os.curdir);
    
    #arcpyScratchWorkspaceFgdbPath = os.path.join(arcpy.env.scratchWorkspace, 'scratch.gdb');
    #arcpy.AddMessage('arcpyScratchWorkspaceFgdbPath: ' + arcpyScratchWorkspaceFgdbPath);
    #print('arcpyScratchWorkspaceFgdbPath: ' + arcpyScratchWorkspaceFgdbPath);    
    #arcpy.env.overwriteOutput = True
    ##arcpy.AddMessage(arcpy.env.overwriteOutput);
        
    # ogr.driver.ags python script tool parameters list
    # inputDataPath - 0
    # inputDataType - 1
    # inputFeatureTypeName - 2
    # outputDataType - 3
    # outputShp - 4
    # outputFgdb - 5
    
    # input data path or url
    inputDataPath = 'http://august-resources.appspot.com/sample.data/geojson.json';  # generic GeoJSON
    # since gdal/ogr 1.8.0 JSON from Esri GeoService REST service is supported
    #inputDataPath = 'http://char:6080/arcgis/rest/services/playground/sanfrancisco/MapServer/0/query?where=TYPE%3D%27Restaurant+%27&text=&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=&returnGeometry=true&maxAllowableOffset=&outSR=4326&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&f=json';
    #inputDataPath = 'http://char:6080/arcgis/services/playground/sanfrancisco/mapserver/wfsserver?SERVICE=WFS'; # OGC WFS        
    #inputDataPath = 'shapefile.shp';
    #inputDataPath = 'csv.csv';
    #inputDataPath = 'gpx.tracks.gpx';
    #inputDataPath = 'georss.simple.xml';
    #inputDataPath = 'georss.gml.xml';
    #inputDataPath = 'svg.cloudmade.small.svg';
    #inputDataPath = arcpy.GetParameterAsText(0);
    #arcpy.AddMessage('inputDataPath' + inputDataPath);
    print('inputDataPath' + inputDataPath)

    
    # input ogr driver type
    inputDriverType = "GeoJSON";
    #inputDriverType = "ESRI Shapefile";
    #inputDriverType = "WFS";                             # since gdal/ogr 1.8.0
    #inputDriverType = "CSV";
    #inputDriverType = "GFT";                             # Google Fusion Table support since gdal/ogr 1.9.0
    #inputDriverType = "GPX";
    #inputDriverType = "GeoRSS";
    #inputDriverType = "SVG";                              # since gdal/ogr 1.9.0
    #inputDriverType = arcpy.GetParameterAsText(1);
    #arcpy.AddMessage('inputDriverType: ' + inputDriverType);
    print('inputDriverType: ' + inputDriverType);
        
    # input feature type name, optional for data source like shape file but required for data source like WFS
    # data sources that do not need inputFeatureTypeName
    #     GeoJSON, CSV, GPX 
    # data sources that do not need inputFeatureTypeName
    #     WFS
    inputFeatureTypeName = "";
    #inputFeatureTypeName = "esri:poi";    #WFS
    # for GPX data source inputFeatureTypeName can be "waypoints", "routes", "tracks", "route_points", or "track_points"
    #inputFeatureTypeName = "tracks";    #GPX
    #inputFeatureTypeName = arcpy.GetParameterAsText(2) # take from user input    
    #arcpy.AddMessage('inputFeatureTypeName: ' + inputFeatureTypeName);
    print('inputFeatureTypeName: ' + inputFeatureTypeName)
    
    # output ogr driver type
    outputDriverType = "ESRI Shapefile";
    #outputDriverType = "FileGDB";
    #outputDriverType = "GeoJSON";
    #outputDriverType = "GeoRSS";
    #outputDriverType = arcpy.GetParameterAsText(3);
    #arcpy.AddMessage('outputDriverType: ' + outputDriverType);
    print('outputDriverType: ' + outputDriverType);    
    
    # TODO: 
    outputDataSourceOpts = [];
    # sample data source creation option for GeoRSS
    #outputDataSourceOpts = ['USE_EXTENSIONS=NO', 'FORMAT=RSS', 'TITLE=GroRSS.ATOM.GML', 'GEOM_DIALECT=GML'];
    # outputDataSourceOpts input from GP service users, it should be multivalue input parameter
    #outputDataSourceOpts = arcpy.GetParameterAsText(4);
    outputPaths = ags_wps_ogr2ogr(str(inputDataPath), str(inputDriverType), str(inputFeatureTypeName), str(outputDriverType), outputDataSourceOpts);

    outputPath = outputPaths[0];
    #arcpy.AddMessage('outputShpPath: ' + outputShpPath);
    print('outputPath: ' + outputPath);

    outputShpPath = outputPaths[1];
    #arcpy.AddMessage('outputShpPath: ' + outputShpPath);
    print('outputShpPath: ' + outputShpPath);
    
    outputFgdbPath = outputPaths[2];
    #arcpy.AddMessage('outputFgdbPath: ' + outputFgdbPath);
    print('outputFgdbPath: ' + outputFgdbPath);
    #arcpy.SetParameterAsText(4, outputShpPath);
    #arcpy.AddMessage('outputShp: ' + outputShpPath);
    print('outputShp: ' + outputShpPath) ;   
    #arcpy.SetParameterAsText(5, outputFgdbPath);
    #arcpy.AddMessage('outputFgdb: ' + outputFgdbPath);
    print('outputFgdb: ' + outputFgdbPath);
