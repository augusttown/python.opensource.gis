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
#arcpy.AddMessage('')
#print ''

global DRIVERTYPE_TO_SUFFIX; 
DRIVERTYPE_TO_SUFFIX = {
    'ESRI Shapefile':     '.shp',
    'FileGDB':            '',
    'GPX':                '.gpx',
    'GeoRSS':             '.xml',
    'GeoJSON':            '.json',
    'SVG':                '.svg'
    # TODO: to add more
};

if __name__ == '__main__':
    
    # set current workspace    
    #os.chdir(r'E:/data/dropbox/Dropbox/Projects/gdal2agswps.python/data/');
    os.chdir(r'/home/ying4682/Dropbox/Projects/gdal2agswps.python/data/');    
    print('os.curdir: ' + os.curdir);
    
    ogr.UseExceptions();
    
    # how many supported ogr drivers
    ogrDriverCount = ogr.GetDriverCount();
    print('ogr.GetDriverCount(): ' + str(ogrDriverCount));
    
    # list each ogr supported driver
    for ogrDriverIdx in range(ogrDriverCount):
        ogrDriver = ogr.GetDriver(ogrDriverIdx);
        ogrDriverName = ogrDriver.GetName();        
        print('ogr driver ' + str(ogrDriverIdx) +  ': ' + str(ogrDriverName));
        
    # how many opened data sources 
    openDSCount = ogr.GetOpenDSCount();    
    print('ogr.GetOpenDSCount(): ' + str(openDSCount))
    # list each opened ogr data sources
    for openDSIdx in range(openDSCount):
        ogrOpenDS = ogr.GetOpenDS(openDSIdx);
        openDSName = ogrOpenDS.GetName();        
        print('ogr openDS ' + str(openDSIdx) +  ': ' + str(openDSName));
    
    # ogr driver type of input data
    inputDriverType = "GeoJSON";
    #inputDriverType = "ESRI Shapefile";
    #inputDriverType = "WFS";                             # since gdal/ogr 1.8.0
    #inputDriverType = "CSV";
    #inputDriverType = "GFT";                             # Google Fusion Table support since gdal/ogr 1.9.0
    #inputDriverType = "GPX";
    #inputDriverType = "GeoRSS";
    #inputDriverType = "SVG";                              # since gdal/ogr 1.9.0    
    print('inputDriverType: ' + inputDriverType);
    
    # url or path of input data
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
    print('inputDataPath' + inputDataPath);
    
    # input feature type name, optional for data source like shape file but required for data source like WFS
    # data sources that do not need inputFeatureTypeName
    #     GeoJSON, CSV, GPX 
    # data sources that do not need inputFeatureTypeName
    #     WFS
    inputFeatureTypeName = "";
    #inputFeatureTypeName = "esri:poi";    #WFS
    # for GPX data source inputFeatureTypeName can be "waypoints", "routes", "tracks", "route_points", or "track_points"
    #inputFeatureTypeName = "tracks";    #GPX    
    print('inputFeatureTypeName: ' + inputFeatureTypeName);
    
    # ogr driver type of output data
    outputDriverType = "ESRI Shapefile";
    #outputDriverType = "FileGDB";
    #outputDriverType = "GeoJSON";
    #outputDriverType = "GeoRSS";  
    print('outputDriverType: ' + outputDriverType);    
    
    # optional string list for data source creation 
    outputDataSourceOpts = [];    # empty    
    #outputDataSourceOpts = ['USE_EXTENSIONS=NO', 'FORMAT=RSS', 'TITLE=GroRSS.ATOM.GML', 'GEOM_DIALECT=GML']; # GeoRSS
    
    # transform output features into another coordinate reference system
    # EPSG:900913
    outputEpsg = '';
    outputWkt = '';
    outputProj4 = '';
    
    
    # input ogr driver
    inputDriver = ogr.GetDriverByName(inputDriverType);    
    print('ogr driver for input data: ' + inputDriverType);
    
    # test driver capability
    #     e.g. can not create/delete data source with WFS driver     
    print('can driver create data source: ' + str(inputDriver.TestCapability(ogr._ogr.ODrCCreateDataSource)));
    print('can driver delete data source: ' + str(inputDriver.TestCapability(ogr._ogr.ODrCDeleteDataSource)));
    
    # output ogr driver
    outputDriver = ogr.GetDriverByName(outputDriverType);    
    print('ogr driver for output data: ' + outputDriverType);

    # output shapefile driver
    # always output as shapefile
    outputShpDriver = ogr.GetDriverByName('ESRI Shapefile');    
    print('ogr driver for output shapefile' + str(outputShpDriver.GetName()));
    
    # output fgdb driver
    # always output as fgdb
    #outputFgdbDriver = ogr.GetDriverByName('FileGDB');    # to support FileGDB gdal/ogr >= 1.9.0
    #print('ogr driver for output fgdb' + str(outputFgdbDriver.GetName()));
    
    # open input data
    inputDataSource = inputDriver.Open(inputDataPath, 0);                 
    print('open data source from: ' + inputDataPath)
        
    # error handling
    if inputDataSource is None:
        print('could not open input data source...exit');
        sys.exit(1);    
    
    # test data source capability
    #     e.g. can not create layer with WFS driver     
    #     QUESTION: so far it always returns false, don't know why
    print('can data source create feature type/layer: ' + str(inputDataSource.TestCapability(ogr._ogr.ODsCCreateLayer)));
    print('can data source delete feature type/layer: ' + str(inputDataSource.TestCapability(ogr._ogr.ODsCDeleteLayer)));        
       
    # data source name
    print('inputDataSource name: ' + str(inputDataSource.GetName()));
    # data source driver name
    print('inputDataSource driver name: ' + str(inputDataSource.GetDriver().GetName()));
    
    # how many feature types/layers in the data source
    featureTypeCount = inputDataSource.GetLayerCount();    
    print('how many feature types in input datasource:' + str(featureTypeCount));
     
    if (inputFeatureTypeName!='') and (inputFeatureTypeName is not None):
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
    
    # featureType is an instance of ogr.Layer      
    if featureType is not None:
        # there are a lot things you can do with a feature type/layer
        print('convert feature type: ' + featureType.GetName());
        
        # instead of getting all the features for a feature type/layer, 
        #     you can set either spatial or attribute filters to filter out features
        # 
        
        # NOTE: set a rectangular spatial filter
        #     api doc: http://gdal.org/python/osgeo.ogr.Layer-class.html#SetSpatialFilterRect        
        #     a sample extent in EPSG:3857 for San Francisco 
        #featureType.SetSpatialFilterRect(-13632076.0218, 4543136.2396, -13626885.0933, 4547124.6364);
        
        # NOTE: set a polygon spatial filter        
        # create a new geometry as spatial filter: polygon with a ring
        #=======================================================================
        # ring = ogr.Geometry(ogr.wkbLinearRing);
        # ring.AddPoint(-13632076.0218, 4543136.2396); #(minx, miny)
        # ring.AddPoint(-13632076.0218, 4547124.6364); #(minx, maxy)
        # ring.AddPoint(-13626885.0933, 4547124.6364); #(maxx, maxy)
        # ring.AddPoint(-13626885.0933, 4543136.2396); #(maxx, miny)
        # # create a polygon geometry
        # poly = ogr.Geometry(ogr.wkbPolygon);
        # poly.AddGeometry(ring);
        # 
        # # set a new polygon geometry spatial filter
        # #     api doc: http://gdal.org/python/osgeo.ogr.Layer-class.html#SetAttributeFilter        
        # #     a sample polygon in EPSG:3857 for San Francisco
        # featureType.SetSpatialFilter(poly);
        #=======================================================================
        
        # NOTE: set an attribute filter
        #     unlike ogr.DataSource.ExecuteSQL(), ogr.Layer.SetAttributeFilter() takes only the query string instead of the whole SQL
        #     the query string should be in the format of an SQL WHERE clause. For instance "population > 1000000 and population < 5000000" where
        #     api doc: http://gdal.org/python/osgeo.ogr.Layer-class.html#SetAttributeFilter
        #featureType.SetAttributeFilter("TYPE = 'Gas'");

        # NOTE: SetIgnoredFields
        #     set which fields can be omitted when retrieving features from the layer.
        #     loaded features will still have those ignored field, but their values are all None
        #featureType.SetIgnoredFields(['ADDRESS']);
        
        try:
            # ogr geometry types
            #===================================================================
            # print('ogr.wkbPoint: ' + str(ogr.wkbPoint));
            # print('ogr.wkbLineString: ' + str(ogr.wkbLineString));
            # print('ogr.wkbLinearRing: ' + str(ogr.wkbLinearRing));
            # print('ogr.wkbPolygon: ' + str(ogr.wkbPolygon));
            # print('ogr.wkbMultiPoint: ' + str(ogr.wkbMultiPoint));
            # print('ogr.wkbMultiLineString: ' + str(ogr.wkbMultiLineString));
            # print('ogr.wkbMultiPolygon: ' + str(ogr.wkbMultiPolygon));            
            # print('ogr.wkbGeometryCollection: ' + str(ogr.wkbGeometryCollection));
            # print('ogr.wkbUnknown: ' + str(ogr.wkbUnknown));
            #===================================================================
            
            # geometry type of feature type/layer
            #print('feature type/layer geometry type: ' + str(featureType.GetGeomType()));
            
            # geometry column of feature type/layer
            # NOTE: This method returns the name of the underlying database column being
            #     used as the geometry column, or "" if not supported. e.g. Shapefile/WFS doesn't support it
            #print('feature type/layer geometry column: ' + str(featureType.GetGeometryColumn()));
            
            # fid column of feature type/layer
            # NOTE: This method returns the name of the underlying database column being
            #     used as the FID column, or "" if not supported.
            #print('feature type/layer fid column: ' + str(featureType.GetFIDColumn()));
            
            # test capabilities of a feature type/layer
            #     api doc: http://gdal.org/python/osgeo.ogr.Layer-class.html#TestCapability
            
            #===================================================================
            # print('feature type/layer capability CreateField: ' + str(featureType.TestCapability(ogr._ogr.OLCCreateField)));
            # print('feature type/layer capability DeleteFeature: ' + str(featureType.TestCapability(ogr._ogr.OLCDeleteFeature)));
            # print('feature type/layer capability FastFeatureCount: ' + str(featureType.TestCapability(ogr._ogr.OLCFastFeatureCount)));
            # print('feature type/layer capability FastGetExtent: ' + str(featureType.TestCapability(ogr._ogr.OLCFastGetExtent)));
            # print('feature type/layer capability FastSetNextByIndex: ' + str(featureType.TestCapability(ogr._ogr.OLCFastSetNextByIndex)));
            # print('feature type/layer capability FastSpatialFilter: ' + str(featureType.TestCapability(ogr._ogr.OLCFastSpatialFilter)));
            # print('feature type/layer capability RandomRead: ' + str(featureType.TestCapability(ogr._ogr.OLCRandomRead)));
            # print('feature type/layer capability RandomWrite: ' + str(featureType.TestCapability(ogr._ogr.OLCRandomWrite)));
            # print('feature type/layer capability SequentialWrite: ' + str(featureType.TestCapability(ogr._ogr.OLCSequentialWrite)));
            # print('feature type/layer capability StringsAsUTF8: ' + str(featureType.TestCapability(ogr._ogr.OLCStringsAsUTF8)));
            # print('feature type/layer capability Transactions: ' + str(featureType.TestCapability(ogr._ogr.OLCTransactions)));            
            #===================================================================
            
            # feature count of feature type/layer
            #print('feature type/layer feature count: ' + str(featureType.GetFeatureCount()));
            
            # extent/mbr of feature type/layer
            #print('feature type/layer extent: ' + str(featureType.GetExtent()));
            
            # default spatial reference
            #     it returns the wkt of the spatial reference
            inputCrs = featureType.GetSpatialRef();
            print('input spatial reference system: ' + str(inputCrs))
            
            # details of the spatial reference system
            #print('input spatial reference system, IsGeographic: ' + str(inputCrs.IsGeographic()));
            #print('input spatial reference system, IsProjected: ' + str(inputCrs.IsProjected()));
            # TODO: there are a lot more you can do with osgeo.osr
            #     api doc: http://gdal.org/python/osgeo.osr.SpatialReference-class.html
            
            # output spatial reference the same as input spatial reference
            # TODO: may take it from geo-processing environment                    
            if inputCrs is None:                
                # some data source like csv may not carry spatial reference system information                
                defaultCrs = osr.SpatialReference()
                #defaultCrs.ImportFromEPSG(4326)     # default to EPSG:4326
                defaultCrs.ImportFromEPSG(900913)    # default to EPSG:900913                
                outputCrs = defaultCrs.Clone(); 
            else:
                outputCrs = inputCrs.Clone();
            
            # create a crs for reprojection                        
            # create any empty spatial reference 
            reprojectCrs900913 = osr.SpatialReference(); 
            reprojectCrs4326 = osr.SpatialReference(); 
            # use osr to populate empty spatial reference system from different sources and formats            
            reprojectCrs900913.ImportFromEPSG(900913); # from an EPSG wkid
            reprojectCrs4326.ImportFromEPSG(4326); # from an EPSG wkid
            
            crsTrans900913 = osr.CoordinateTransformation(outputCrs, reprojectCrs900913);
            crsTrans4326 = osr.CoordinateTransformation(outputCrs, reprojectCrs4326);
            
            #reprojectCrs900913.ImportFromEPSGA(900913); # from an EPSGA (EPSG Authentic or any other "a" word implying it sticks stickly to the rules) wkid
            # import from a url 
            #     see sample: http://svn.osgeo.org/gdal/trunk/autotest/osr/osr_url.py
            #     it probably takes url that points to a wkt, proj4, ESRI, string
            #     http://spatialreference.org/ref/epsg/4267/ogcwkt/
            #reprojectCrs900913.ImportFromUrl('http://spatialreference.org/ref/epsg/4267/ogcwkt/');
            # import from a wkt string
            #reprojectCrs900913.ImportFromWkt('PROJCS["Google Maps Global Mercator",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Mercator_2SP"],PARAMETER["standard_parallel_1",0],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",0],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["Meter",1],EXTENSION["PROJ4","+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs"],AUTHORITY["EPSG","900913"]]');
            # import from an ESRI wkt string
            #reprojectCrs900913.ImportFromESRI('PROJCS["Google_Maps_Global_Mercator",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Mercator_2SP"],PARAMETER["standard_parallel_1",0],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",0],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["Meter",1]]'); 
            # import from a proj4 string
            #reprojectCrs900913.ImportFromESRI('+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs');
            
            
            #use osr to convert a sptial reference object into different format e.g. esri, wkt, proj4 etc.
            #print('EPSG:900913 in wkt format: ' + reprojectCrs900913.ExportToWkt());
            #print('EPSG:900913 in pretty wkt format: ' + reprojectCrs900913.ExportToPrettyWkt());
            #print('EPSG:900913 in proj4 format: ' + reprojectCrs900913.ExportToProj4());
            #print('EPSG:900913 in pci format: ' + reprojectCrs900913.ExportToPCI());    # returns a list
            #print('EPSG:900913 in usgs format: ' + reprojectCrs900913.ExportToUSGS());    # returns a list
            #print('EPSG:900913 in xml format: ' + reprojectCrs900913.ExportToXML());
            
            # convert to ESRI compatible format
            #reprojectCrs900913.MorphToESRI();
            #print('EPSG:900913 in esri wkt format: ' + reprojectCrs900913.ExportToWkt());
            #reprojectCrs900913.MorphFromESRI();
            #print('EPSG:900913 in standard wkt format again: ' + reprojectCrs900913.ExportToWkt());                        
                                
            print('output spatial reference system' + str(outputCrs))
                                                    
            # create output shapefile/fgdb in current directory                                                 
            # rename shapefile output
            # TODO: obtain the dynamic scratchworkspace path when running as GP service in ArcGIS Server
                                              
            outputPath = "../scratch/output" + DRIVERTYPE_TO_SUFFIX[outputDriverType];
            # TODO: define a global hash to map driver name to output feature type name
            outputFeatureTypeName = 'output'
                    
            # without giving .shp suffix, a folder will be created to contain the output shapefile 
            outputShpPath = '../scratch/outputShpForAgs' + DRIVERTYPE_TO_SUFFIX['ESRI Shapefile'];                                             
            #outputShpPath = '%scratchworkspace%/' + 'outputShpForAgs'          # doing ArcGIS Server GP way, so other tools/modules can take this as input
            outputShpFeatureTypeName = 'outputShpForAgs'
                    
            outputFgdbPath = '../scratch/outputFgdbForAgs' + DRIVERTYPE_TO_SUFFIX['FileGDB'];
            #outputFgdbPath = '%scratchworkspace%/scratch.gdb/outputFgdb'
            outputFgdbFeatureTypeName = 'outputFgdbForAgs'
                    
            # remove existing user defined output
            if os.path.exists(outputPath):                                      # test if file already exists
                outputDriver.DeleteDataSource(outputPath)                       # if exists, delete it                        
                print('delete existing output data');
                    
            # remove existing shapefile output
            if os.path.exists(outputShpPath):                                      # test if file already exists
                outputShpDriver.DeleteDataSource(outputShpPath)                       # if exists, delete it
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
            outputDataSource = outputDriver.CreateDataSource(outputPath, dataSourceOpts);         
            if outputDataSource is None:                        
                print('could not create output data source' + outputPath)
                sys.exit(1);
            
            # create output shapefile with the same geometry type as WFS feature type
            print('create output data source: ' + outputPath);
                    
            outputShpDataSource = outputShpDriver.CreateDataSource(outputShpPath);              
            if outputShpDataSource is None:
                print('could not create output shapefile data source' + outputShpPath);
                sys.exit(1);
            
            # create output shapefile with the same geometry type as WFS feature type
            print('create output shapefile data source: ' + outputShpPath);
                                                        
            # feature type feature definition
            featureTypeDef = featureType.GetLayerDefn() 
            # featureType.GetLayerDefn() returns the schema of feature type/layer
            # TODO: what you can do with featureTypeDef
            #print('feature type defintion name: ' + str(featureTypeDef.GetName()));
            # GetFieldIndex('') can be called to look for a field by name
            #print('reference count of feature type: ' + str(featureTypeDef.GetReferenceCount()));
            #print('can geometry omitted when fetching feature: ' + str(featureTypeDef.IsGeometryIgnored()));
            #print('can style omitted when fetching feature: ' + str(featureTypeDef.IsStyleIgnored()));
                                   
            # feature type geometry type definition     
            featureTypeGeomDef = featureTypeDef.GetGeomType()
            print('input feature type geometry: ' + str(featureTypeGeomDef));                    
            print('output feature type geometry: ' + str(featureTypeGeomDef));
                                    
            # create output feature type
            outputFeatureType = outputDataSource.CreateLayer(outputFeatureTypeName, geom_type=featureTypeGeomDef)
            # create output shapefile feature type
            outputShpFeatureType = outputShpDataSource.CreateLayer(outputShpFeatureTypeName, geom_type=featureTypeGeomDef)
                    
            # clone attribute fields
            # the list of attribute fields includes the geometry field
            featureTypeFieldCount = featureTypeDef.GetFieldCount();
            
            for featureTypeFieldIdx in range(featureTypeFieldCount):
                featureTypeField = featureTypeDef.GetFieldDefn(featureTypeFieldIdx)
                # featureTypeDef.GetFieldDefn() returns the schema of a field in feature type/layer
                # TODO: what you can do with field definition
                #print('is field type ignored: ' + str(featureTypeField.IsIgnored()));    # return '0' means true
                #print('field type name: ' + str(featureTypeField.GetTypeName()));   # type name like 'String', 'int' etc.
                #print('field type Precision: ' + str(featureTypeField.GetPrecision()));
                #print('field type width: ' + str(featureTypeField.GetWidth()));     # field width or else?   
                                
                # create output feature type field
                outputFeatureType.CreateField(featureTypeField)
                # create output shapefile feature type field
                outputShpFeatureType.CreateField(featureTypeField)                
                print('create output feature type field: ' + str(featureTypeField.GetName()) + '[' + str(featureTypeField.GetType()) + ']') 
            # output feature type definition
            outputFeatureTypeDef = outputFeatureType.GetLayerDefn()
            # output shapefile feature type definition
            outputShpFeatureTypeDef = outputShpFeatureType.GetLayerDefn()
                    
            # ogr.Layer.ResetReading(): reset feature reading to start on the first feature.
            #     this affects GetNextFeature()
            # loop through each feature
            #featureType.ResetReading();
            feature = featureType.GetNextFeature();
                    
            while feature:
                outputFeature = ogr.Feature(outputFeatureTypeDef)
                outputShpFeature = ogr.Feature(outputShpFeatureTypeDef)
                        
                # TODO: you may need to create geometry field manually from non-spatial fields
                #     e.g. CSV  
                outputFeatureGeom = feature.GetGeometryRef()
                outputShpFeatureGeom = feature.GetGeometryRef()
                
                # if you need to do reprojection, do it right here
                # use Geometry.Transform(CoordinateTransformation)
                # TODO: for reason reprojection raises exception here
                #     argument 2 of type 'OSRCoordinateTransformationShadow *'
                #outputShpFeatureGeom.Transform(crsTrans900913);
                #outputShpFeatureGeom.Transform(crsTrans4326);
                
                # it seems that if the coordinate values are in scientific notation OGR has problem
                #x = str(outputFeatureGeom.GetX())
                #y = str(outputFeatureGeom.GetY())    
                #print x + "," + y 
                                                   
                outputFeature.SetGeometry(outputFeatureGeom)
                outputShpFeature.SetGeometry(outputShpFeatureGeom)
                                                
                #print 'set output feature geometry type' 
                        
                # loop through attributes for each feature 
                for featureTypeFieldIdx in range(featureTypeFieldCount):
                    outputFeature.SetField(featureTypeFieldIdx, feature.GetField(featureTypeFieldIdx))
                    outputShpFeature.SetField(featureTypeFieldIdx, feature.GetField(featureTypeFieldIdx))
                #print 'set output feature attributes'     
                        
                # create a new feature
                outputFeatureType.CreateFeature(outputFeature)
                outputShpFeatureType.CreateFeature(outputShpFeature) 
                #print('create output feature')
                        
                # destroy temporary features
                outputFeature.Destroy
                outputShpFeature.Destroy
                feature.Destroy
                # loop to the next feature
                feature = featureType.GetNextFeature()                            
                                            
            # morph to be ESRI compatible
            outputCrs.MorphToESRI() 
                    
            print('convert projection wkt to esri format')       
            #print str(outputCrs)
                    
            # write out .prj file                            
            # if it is shape file, generate .prj file                          
            if outputDriverType == 'ESRI Shapefile':                        
                outputFeatureTypePrjPath = outputPath.replace('.shp', '.prj')
                if os.path.exists(outputFeatureTypePrjPath):                                    # test if file already exists
                    # TODO: how to delete a file in python 
                    print('delete existing .prj file')                         
                # generate new .prj file
                outputFeatureTypePrj = open(outputFeatureTypePrjPath, 'w')
                outputFeatureTypePrj.write(outputCrs.ExportToWkt())
                outputFeatureTypePrj.close()
                print('create new .prj file')
                    
            # write out .prj file for shapefile output    
            outputShpFeatureTypePrjPath = outputShpPath.replace('.shp', '.prj')
            if os.path.exists(outputShpFeatureTypePrjPath):                                    # test if file already exists
                # TODO: how to delete a file in python                    
                print('delete existing .prj file')                         
            # generate new .prj file
            outputShpFeatureTypePrj = open(outputShpFeatureTypePrjPath, 'w');
            outputShpFeatureTypePrj.write(outputCrs.ExportToWkt());
            outputShpFeatureTypePrj.close();
                
            print('create new .prj file');
                
            # destroy output data source
            outputDataSource.Destroy();
            outputShpDataSource.Destroy();

            # copy output shapefile to fgdb
            print('call CopyFeatures_management gp tool')                    
            #arcpy.CopyFeatures_management(outputShpPath, '%scratchworkspace%/scratch.gdb/outputFgdb')                                
            
            # release ResultSet created by ExecuteSQL() from data source            
            #inputDataSource.ReleaseResultSet(featureType);
                
        except ValueError:
            # do nothing
            print('...error...');
            
    else:
        print('no match feature type or layer found...exit');

    # it seems that Release() has the same effect as Destroy()
    # release the input data source
    #inputDataSource.Release();
    # destroy input data source
    inputDataSource.Destroy();
    