# import modules
import os
import sys
# import gdal/ogr modules
from osgeo import ogr
from osgeo import osr

# set current workspace
os.chdir(r'C:/yingqi/nightingale/projects/python.opensource.gis/src/github/python.opensource.gis/gdal2agswps/scratch/')

# get the shapefile driver
shp_driver = ogr.GetDriverByName('ESRI Shapefile')
# get the WFS driver
wfs_driver = ogr.GetDriverByName('WFS')

# open the data source
# to open a WFS data source
#     'WFS:http://<WFS_URL>?SERVICE=WFS [?OPTIONAL_TYPENAME=VALUE[&OPTIONNAL_PARAMETER2=VALUE]]
#     Q: How to request features from WFS in a non-default coordinate reference system???
wfs_datasource = wfs_driver.Open('http://gouf:6080/arcgis/services/playground/haiti_3857/MapServer/WFSServer?SERVICE=WFS', 0)
#datasource = driver.Open('http://localhost:8080/geoserver-2.1-snapshot-10282010/wfs?SERVICE=WFS esri:sf_pizzastores_900913', 0)
# feature types from WFS that will be converted to shape file
fs_to_output = ['esri:buildings','esri:places','esri:roads','esri:provinces']
#fs_to_output = ['esri:sf_pizzastores_900913','esri:sf_highways_900913','esri:sf_blockgroups_900913']

# error handling
if wfs_datasource is None:
    print 'Could not open WFS'
    sys.exit(1)

# always get the first layer 
#layer = datasource.GetLayer()

# layers in WFS data source
wfs_fs_count = wfs_datasource.GetLayerCount();
#print 'WFS feature types count: ' + str(layer_count) 
if wfs_fs_count >= 0:
    # loop through each layer
    for wfs_fs_idx in range(wfs_fs_count):
        # get the data layer
        wfs_fs = wfs_datasource.GetLayer(wfs_fs_idx)               

        try:
            if fs_to_output.index(wfs_fs.GetName())>=0:
                print 'include WFS feature type: ' + wfs_fs.GetName()
                
                if wfs_fs is not None:
                    print 'found WFS feature type: ' + wfs_fs.GetName()
                    #print wfs_fs.GetName()
                    wfs_fs_name = wfs_fs.GetName()            
                    
                    # get default spatial reference
                    wfs_default_sr = wfs_fs.GetSpatialRef()
                    #print str(wfs_default_sr)
                    # create output shape file spatial reference from default WFS spatial reference
                    shp_sr = wfs_default_sr.Clone() 
                    # for test only, it will be morph later before output to .prj file
                    #shp_sr.MorphToESRI()
                    #print str(shp_sr)  
                    
                    # create output shapefile in current directory             
                    shp_path = wfs_fs.GetName().replace(':', '_');                  # replace ':' in namespace with '_'                    
                    shp_path = shp_path + "_shp.shp"
                    if os.path.exists(shp_path):                                    # test if file already exists
                        shp_driver.DeleteDataSource(shp_path)                       # if exists, delete it
                    # create output shape file data source
                    shp_datasource = shp_driver.CreateDataSource(shp_path)              
                    if shp_datasource is None:
                        print 'Could not create shape file' + shp_path
                        sys.exit(1)
                    # create output shapefile with the same geometry type as WFS feature type
                    print 'create output shapefile: ' + shp_path
                                
                    # get WFS feature type feature definition
                    wfs_fs_lyrDef = wfs_fs.GetLayerDefn()            
                    # get WFS feature type geometry type     
                    shp_fs_geomDef = wfs_fs_lyrDef.GetGeomType()
                    #print 'WFS feature type geometry: ' + str(shp_fs_geomDef)
                    print 'output shape file geometry: ' + str(shp_fs_geomDef)
                                
                    # create output shapefile
                    shp_fs = shp_datasource.CreateLayer(shp_path, geom_type=shp_fs_geomDef)
                    
                    # clone attribute fields
                    #   the list of attribute fields does include the geometry field
                    wfs_fld_count = wfs_fs_lyrDef.GetFieldCount()
                    for wfs_fld_idx in range(wfs_fld_count):
                        wfs_fld = wfs_fs_lyrDef.GetFieldDefn(wfs_fld_idx)
                        # create output shape file field
                        shp_fs.CreateField(wfs_fld)
                        print 'create output shape file field: ' + str(wfs_fld.GetName()) + '[' + str(wfs_fld.GetType()) + ']' 
                    # get the shape file layer definition
                    shp_fs_def = shp_fs.GetLayerDefn()
                    
                    wfs_in_feature = wfs_fs.GetNextFeature()
                    while wfs_in_feature:
                        shp_out_feature = ogr.Feature(shp_fs_def)
                        shp_out_feature_geom = wfs_in_feature.GetGeometryRef()
                        
                        # it seems that if the coordinate values are in scientific notation OGR has problem
                        #x = str(shp_out_feature_geom.GetX())
                        #y = str(shp_out_feature_geom.GetY())    
                        #print x + "," + y
                        
                        shp_out_feature.SetGeometry(shp_out_feature_geom)
                        
                        for wfs_fld_idx in range(wfs_fld_count):
                            shp_out_feature.SetField(wfs_fld_idx, wfs_in_feature.GetField(wfs_fld_idx))
                        
                        shp_fs.CreateFeature(shp_out_feature)
                        shp_out_feature.Destroy
                        wfs_in_feature.Destroy
                        wfs_in_feature = wfs_fs.GetNextFeature()                            
                                        
                    # morph to be ESRI compatible
                    shp_sr.MorphToESRI()        
                    #print str(shp_sr)
                    # write out .prj file
                    
                    shp_fs_prj_path = shp_path.replace('.shp', '.prj')
                    #if os.path.exists(shp_fs_prj_path):                                    # test if file already exists
                        # how to delete a file in python 
                    shp_fs_prj = open(shp_fs_prj_path, 'w')
                    shp_fs_prj.write(shp_sr.ExportToWkt())
                    shp_fs_prj.close()
                    
                    # why destory feature here raises exception???
                    #feature.Destory
                    shp_datasource.Destroy() 
                
                
        except ValueError:
            # do nothing
            print 'skip WFS feature type: ' + wfs_fs.GetName()
             
        
        

# close the data source and text file
wfs_datasource.Destroy()
