# import system modules
import os
import sys
import string
#
# import gdal/ogr modules
from osgeo import ogr
from osgeo import osr
#
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
        
def copy_shp_ogr(inputDataPath, inputDriverType, inputFeatureTypeName, outputDriverType, outputFeatureTypeName, outputDataSourceOpts):        
    # input ogr driver
    inputDriver = ogr.GetDriverByName(inputDriverType)    
    print('ogr driver for input dataset: ' + inputDriverType);
        
    # output ogr driver
    outputDriver = ogr.GetDriverByName(outputDriverType);
    print('ogr driver for output dataset: ' + outputDriverType);

    # output shapefile driver
    # always output as shapefile
    outputShpDriver = ogr.GetDriverByName('ESRI Shapefile');       
    # output fgdb driver
    # always output as fgdb
    outputFgdbDriver = ogr.GetDriverByName('FileGDB');
    
    # open input data        
    inputDataSource = inputDriver.Open(inputDataPath, 0);                 
    print('open input data source: ' + inputDataPath);
        
    # error handling
    if inputDataSource is None:
        print('could not open input data source');
        sys.exit(1);
    
    # feature type count
    # for data source like WFS there can be more than 1 layer
    featureTypeCount = inputDataSource.GetLayerCount();
    print('feature type count:' + str(featureTypeCount));
    
    if(inputFeatureTypeName!='') and (inputFeatureTypeName is not None):
        # look for feature type/layer by name
        featureType = inputDataSource.GetLayerByName(inputFeatureTypeName);
    else:
        # assume there is only one feature type/layer in the data source
        featureType = inputDataSource.GetLayer(0);   
          
    if featureType is not None:        
        print('process feature type: ' + featureType.GetName());        
        try:
            # default spatial reference
            inputCrs = featureType.GetSpatialRef();
            print('input feature type spatial reference system: ' + str(inputCrs));
            # output spatial reference the same as input spatial reference
            # TODO: may take it from geo-processing environment                    
            if inputCrs is None:
                # some data source like csv may not carry spatial reference system information
                defaultCrs = osr.SpatialReference();
                defaultCrs.ImportFromEPSG(4326);     # default to EPSG:4326
                #defaultCrs.ImportFromEPSG(900913);    # default to EPSG:900913
                outputCrs = defaultCrs.Clone();
            else:
                outputCrs = inputCrs.Clone(); 
            
            print('output feature type spatial reference system: ' + str(outputCrs));                                            
            #
            outputPath = outputFeatureTypeName + driverTypeToFileSuffix[outputDriverType];                    
            #                        
            # remove existing user defined output
            if os.path.exists(outputPath):                                       # test if file already exists
                outputDriver.DeleteDataSource(outputPath);                       # if exists, delete it                
                print('delete existing output data');
            
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
                print('could not create output data source' + outputPath);
                sys.exit(1);
            #            
            print('create output data source: ' + outputPath);
                                             
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
            
            # clone attribute fields
            #   the list of attribute fields includes the geometry field
            featureTypeFieldCount = featureTypeDef.GetFieldCount();
            for featureTypeFieldIdx in range(featureTypeFieldCount):
                featureTypeField = featureTypeDef.GetFieldDefn(featureTypeFieldIdx);
                # create output feature type field
                outputFeatureType.CreateField(featureTypeField);                
                print('create output feature type field: ' + str(featureTypeField.GetName()) + '[' + str(featureTypeField.GetType()) + ']'); 
            # output feature type definition
            outputFeatureTypeDef = outputFeatureType.GetLayerDefn();
            # loop through each feature
            feature = featureType.GetNextFeature();
            
            while feature:
                outputFeature = ogr.Feature(outputFeatureTypeDef);                
                # TODO: you may need to create geometry field manually from non-spatial fields
                #     e.g. CSV  
                outputFeatureGeom = feature.GetGeometryRef();                
                # it seems that if the coordinate values are in scientific notation OGR has problem
                #x = str(outputFeatureGeom.GetX());
                #y = str(outputFeatureGeom.GetY());                                                               
                outputFeature.SetGeometry(outputFeatureGeom);                                                
                #print('set output feature geometry type');                 
                # loop through attributes for each feature 
                for featureTypeFieldIdx in range(featureTypeFieldCount):
                    
                    fieldName = str((featureTypeDef.GetFieldDefn(featureTypeFieldIdx)).GetName());
                    # really need a regular expression
                    if fieldName == 'streetname':
                        # 
                        fieldValue = str(feature.GetField(featureTypeFieldIdx)).lower().replace(' ', '');
                        #
                        if fieldValue.find('40th')!=-1:
                            streetNameValue = '40th';
                        elif fieldValue.find('39th') != -1:
                            streetNameValue = '39th';
                        elif fieldValue.find('38th') != -1:
                            streetNameValue = '38th';
                        elif fieldValue.find('37th') != -1:
                            streetNameValue = '37th';
                        elif fieldValue.find('36th') != -1:
                            streetNameValue = '36th';
                        elif fieldValue.find('35th') != -1:
                            streetNameValue = '35th';
                        elif fieldValue.find('34th') != -1:
                            streetNameValue = '34th';
                        elif fieldValue.find('33rd') != -1:
                            streetNameValue = '33rd';
                        elif fieldValue.find('32nd') != -1:
                            streetNameValue = '32nd';
                        elif fieldValue.find('31st') != -1:
                            streetNameValue = '31st';
                        elif fieldValue.find('30th')!=-1:
                            streetNameValue = '30th';
                        elif fieldValue.find('29th') != -1:
                            streetNameValue = '29th';
                        elif fieldValue.find('28th') != -1:
                            streetNameValue = '28th';
                        elif fieldValue.find('27th') != -1:
                            streetNameValue = '27th';
                        elif fieldValue.find('26th') != -1:
                            streetNameValue = '26th';
                        elif fieldValue.find('25th') != -1:
                            streetNameValue = '25th';
                        elif fieldValue.find('24th') != -1:
                            streetNameValue = '24th';
                        elif fieldValue.find('23rd') != -1:
                            streetNameValue = '23rd';
                        elif fieldValue.find('22nd') != -1:
                            streetNameValue = '22nd';
                        elif fieldValue.find('21st') != -1:
                            streetNameValue = '21st';
                        elif fieldValue.find('20th') != -1:
                            streetNameValue = '20th';
                        elif fieldValue.find('19th') != -1:
                            streetNameValue = '19th';
                        elif fieldValue.find('18th') != -1:
                            streetNameValue = '18th';
                        elif fieldValue.find('17th') != -1:
                            streetNameValue = '17th';
                        elif fieldValue.find('16th') != -1:
                            streetNameValue = '16th';
                        elif fieldValue.find('15th') != -1:
                            streetNameValue = '15th';
                        elif fieldValue.find('14th') != -1:
                            streetNameValue = '14th';
                        elif fieldValue.find('13th') != -1:
                            streetNameValue = '13th';
                        elif fieldValue.find('12th') != -1:
                            streetNameValue = '12th';
                        elif fieldValue.find('11th') != -1:
                            streetNameValue = '11th';
                        elif fieldValue.find('10th') != -1:
                            streetNameValue = '10th';
                        elif fieldValue.find('9th') != -1:
                            streetNameValue = '9th';
                        elif fieldValue.find('8th') != -1:
                            streetNameValue = '8th';
                        elif fieldValue.find('7th') != -1:
                            streetNameValue = '7th';
                        elif fieldValue.find('6th') != -1:
                            streetNameValue = '6th';
                        elif fieldValue.find('5th') != -1:
                            streetNameValue = '5th';
                        elif fieldValue.find('4th') != -1:                            
                            streetNameValue = '4th';
                        elif fieldValue.find('3rd') != -1:
                            streetNameValue = '3rd';
                        elif fieldValue.find('2nd') != -1:
                            streetNameValue = '2nd';
                        elif fieldValue.find('1st') != -1:
                            streetNameValue = '1st';
                        else:
                            streetNameValue = feature.GetField(featureTypeFieldIdx);
                        #        
                        outputFeature.SetField(featureTypeFieldIdx, streetNameValue);                       
                        #print (fieldValue + ' , ' + streetNameValue);
                    elif fieldName == 'streettype':
                        # 
                        fieldValue = str(feature.GetField(featureTypeFieldIdx)).upper().replace(' ', '');
                        # the mapping is based on U.S. State and Street Postal Abbreviations 
                        #     http://www.realifewebdesigns.com/web-marketing/abbreviations-states-streets.asp
                        #     http://pe.usps.com/text/pub28/28apc_001.html
                        if fieldValue.find('AVE') != -1:
                            streetTypeValue = 'Avenue';
                        elif fieldValue.find('BLVD') != -1:
                            streetTypeValue = 'Boulevard';
                        elif fieldValue.find('CIR') != -1:
                            streetTypeValue = 'Circle';
                        elif fieldValue.find('CT') != -1:
                            streetTypeValue = 'Court';
                        elif fieldValue.find('CTR') != -1:
                            streetTypeValue = 'Center';
                        elif fieldValue.find('DR') != -1:
                            streetTypeValue = 'Drive';
                        elif fieldValue.find('EXPY') != -1:
                            streetTypeValue = 'Expressway';
                        elif fieldValue.find('FWY') != -1:
                            streetTypeValue = 'Freeway';
                        elif fieldValue.find('HWY') != -1:
                            streetTypeValue = 'Highway';
                        elif fieldValue.find('LN') != -1:
                            streetTypeValue = 'Lane';
                        elif fieldValue.find('PKWY') != -1:
                            streetTypeValue = 'Parkway';
                        elif fieldValue.find('PL') != -1:
                            streetTypeValue = 'Place';
                        elif fieldValue.find('RD') != -1:
                            streetTypeValue = 'Road';
                        elif fieldValue.find('RTE') != -1:
                            streetTypeValue = 'Route';
                        elif fieldValue.find('ST') != -1:
                            streetTypeValue = 'Street';
                        elif fieldValue.find('TER') != -1:
                            streetTypeValue = 'Terrace';
                        elif fieldValue.find('WY') != -1:
                            streetTypeValue = 'Way';
                        else:  
                            # 
                            streetTypeValue = '';  
                    else:
                        outputFeature.SetField(featureTypeFieldIdx, feature.GetField(featureTypeFieldIdx));
                                                                        
                # create a new feature
                outputFeatureType.CreateFeature(outputFeature);                
                #print('create output feature');
                
                # destroy temporary features
                outputFeature.Destroy;
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
              
            # destroy output data source
            outputDataSource.Destroy();                             
            #             
            # destroy input data source
            inputDataSource.Destroy();
            # return output paths
            return [outputPath];
                            
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
    #os.chdir(r'E:/data/dropbox/Dropbox/Projects/gdal2agswps.python/scratch/');
    #os.chdir(r'E:/data/dropbox/Dropbox/Projects/gdal2agswps.python/data/');
    #os.chdir(r'/home/ying4682/Dropbox/Projects/gdal2agswps.python/data/');    
    os.chdir(r'/home/ying4682/Dropbox/Projects/osm.contribution/shp/rancho.cucamonga/');
    
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
    #inputDataPath = 'http://august-resources.appspot.com/sample.data/geojson.json';  # generic GeoJSON
    # since gdal/ogr 1.8.0 JSON from Esri GeoService REST service is supported
    #inputDataPath = 'http://char:6080/arcgis/rest/services/playground/sanfrancisco/MapServer/0/query?where=TYPE%3D%27Restaurant+%27&text=&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=&returnGeometry=true&maxAllowableOffset=&outSR=4326&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&f=json';
    #inputDataPath = 'http://char:6080/arcgis/services/playground/sanfrancisco/mapserver/wfsserver?SERVICE=WFS'; # OGC WFS        
    inputDataPath = 'parcel_4326_1m_simplified_ags.shp';
    #inputDataPath = 'csv.csv';
    #inputDataPath = 'gpx.tracks.gpx';
    #inputDataPath = 'georss.simple.xml';
    #inputDataPath = 'georss.gml.xml';
    #inputDataPath = 'svg.cloudmade.small.svg';
    #inputDataPath = arcpy.GetParameterAsText(0);
    #arcpy.AddMessage('inputDataPath' + inputDataPath);
    print('inputDataPath' + inputDataPath)

    
    # input ogr driver type
    #inputDriverType = "GeoJSON";
    inputDriverType = "ESRI Shapefile";
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
 
    # output feature type name
    outputFeatureTypeName = 'parcel_4326_attributes_formatted';
 
    outputPaths = copy_shp_ogr(str(inputDataPath), str(inputDriverType), str(inputFeatureTypeName), str(outputDriverType), str(outputFeatureTypeName), outputDataSourceOpts);
    outputPath = outputPaths[0];
    #arcpy.AddMessage('outputShpPath: ' + outputShpPath);
    print('outputPath: ' + outputPath);