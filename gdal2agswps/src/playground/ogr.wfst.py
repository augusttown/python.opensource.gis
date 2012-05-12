# import modules
import os
import sys
# import gdal/ogr modules
from osgeo import ogr
from osgeo import osr

# set current workspace
os.chdir(r'C:/yingqi/nightingale/projects/python.opensource.gis/src/github/python.opensource.gis/gdal2agswps/scratch/')

# get the WFS driver
wfsDriver = ogr.GetDriverByName('WFS')

# open source WFS data source in update('1') mode 
#wfsFromDatasource = wfsDriver.Open('http://gouf:6080/arcgis/services/playground/buildings_from_sde/MapServer/WFSServer?SERVICE=WFS', 1)
wfsFromDatasource = wfsDriver.Open('http://gouf:6080/arcgis/services/playground/buildings_to_sde/MapServer/WFSServer?SERVICE=WFS', 1)
# open target WFS data source in update('1') mode
#wfsToDatasource = wfsDriver.Open('http://gouf:6080/arcgis/services/playground/buildings_to_sde/MapServer/WFSServer?SERVICE=WFS', 1)
wfsToDatasource = wfsDriver.Open('http://gouf:6080/arcgis/services/playground/buildings_from_sde/MapServer/WFSServer?SERVICE=WFS', 1)

if wfsFromDatasource is None:
    print 'could not open source WFS'
    sys.exit(1)
    
if wfsToDatasource is None:
    print 'could not open target WFS'
    sys.exit(1)

# specify the list of feature types to insert/update/delete
fromWfsLyrName = 'esri:buildings'
toWfsLyrName = 'esri:buildings'

fromWfsLyr = wfsFromDatasource.GetLayerByName(fromWfsLyrName)
toWfsLyr = wfsToDatasource.GetLayerByName(toWfsLyrName)

if fromWfsLyr is None:
    print 'could not open WFS feature type: ' + fromWfsLyrName
    sys.exit(1)
    
if toWfsLyr is None:
    print 'could not open WFS feature type: ' + toWfsLyrName
    sys.exit(1)
    
fromWfsFeature = fromWfsLyr.GetNextFeature()
#print 'Features from source WFST: '
# is fromWfsLyr.GetFeatureCount() heavy?
while fromWfsFeature:
    fromFid = fromWfsFeature.GetFID()
    print 'Source WFS feature FID: ' + str(fromFid)    
    if fromFid >= 0 and fromWfsFeature is not None:
        # insert the feature from source WFST to target WFST
        gmlIdFldIdx = fromWfsFeature.GetFieldIndex('gml_id')
        nameFldIdx = fromWfsFeature.GetFieldIndex('Name')
        
        # check if 'gml_id' field a feature is set or not
        #print fromWfsFeature.IsFieldSet(gmlIdFldIdx)
        # feature cannot be inserted into target WFST if 'gml_id' is already set, so unset it
        if fromWfsFeature.IsFieldSet(gmlIdFldIdx) is True: 
            fromWfsFeature.UnsetField(gmlIdFldIdx)
        #print fromWfsFeature.IsFieldSet(gmlIdFldIdx)
        # why clone() fails on a feature from source WFST
        #print '    clone feature'            
        #cloneFeature = fromWfsFeature.clone()
        print '    insert feature into target WFST'
        toWfsLyr.CreateFeature(fromWfsFeature)
        
        # update the feature from source WFST
        print '    update from source WFST'
        fromWfsFeature.SetField(nameFldIdx, 'name udpated ' + str(fromFid))
        fromWfsLyr.SetFeature(fromWfsFeature)        
        
        # delete the feature from source WFST
        #print '    delete from source WFST'
        #fromWfsLyr.DeleteFeature(fromFid)
        
    #
    fromWfsFeature = fromWfsLyr.GetNextFeature()

# reset feature reading to start on target WFST. 
toWfsLyr.ResetReading()   
toWfsFeature = toWfsLyr.GetNextFeature()
#print 'Features from target WFST: '
# is toWfsFeature.GetFeatureCount() heavy?
while toWfsFeature:
    toFid = toWfsFeature.GetFID()
    print 'Target WFS feature FID: ' + str(toFid)    
    # TODO:
    toWfsFeature = toWfsLyr.GetNextFeature()
     
#
wfsFromDatasource.Destroy()
wfsToDatasource.Destroy()

