#!/usr/bin/python

"""
This script is designed to act as assistance in converting shapefiles
to OpenStreetMap data. This file is optimized and tested with MassGIS
shapefiles, converted to EPSG:4326 before being passed to the script.
You can perform this conversion with 

   ogr2ogr -t_srs EPSG:4326 new_file.shp old_file.shp

It is expected that you will modify the fixed_tags, tag_mapping, and
boring_tags attributes of this script before running. You should read,
or at least skim, the code up until it says:

  DO NOT CHANGE AFTER THIS LINE.

to accomodate your own data. 
"""

__author__ = "Christopher Schmidt <crschm...@crschmidt.net>, Emilie Laffray <emilie.laff...@gmail.com>"
__version__ = "$Id$"

gdal_install = """
Installing GDAL depends on your platform. Information is available at:
   
   http://trac.osgeo.org/gdal/wiki/DownloadingGdalBinaries

For Debian-based systems:

   apt-get install python-gdal

will usually suffice. 
"""

import time

# These tags are attached to all exterior ways. You can put any key/value pairs
# in this dictionary. 

fixed_tags = {
    'source': 'San Bernardino County Assessor Office http://gis.sbcounty.gov/default.aspx',
    'area': 'yes',
    'created_by': 'polyshp2osm'
}  

# TODO: is there a way to store this in a file and load it everytime the script is run?
typeuseToLanduse = {
    0    : "vacant",
    1    : "other",
    2    : "other",
    3    : "other",
    4    : "cemetery",
    100    : "industrial",
    101    : "industrial",
    102    : "industrial",
    103    : "industrial",
    104    : "industrial",
    105    : "industrial",
    106    : "industrial",
    110    : "industrial",
    111    : "industrial",
    112    : "industrial",
    113    : "industrial",
    114    : "industrial",
    115    : "industrial",
    116    : "industrial",
    140    : "industrial",
    141    : "industrial",
    142    : "industrial",
    143    : "industrial",
    150    : "industrial",
    151    : "industrial",
    152    : "industrial",
    153    : "industrial",
    160    : "industrial",
    161    : "industrial",
    162    : "industrial",
    163    : "industrial",
    164    : "industrial",
    170    : "industrial",
    171    : "industrial",
    172    : "industrial",
    173    : "industrial",
    174    : "industrial",
    180    : "industrial",
    210    : "commercial",
    211     : "commercial",
    212    : "commercial",
    230     : "commercial",
    231    : "commercial",
    232     : "commercial",
    233    : "commercial",
    234    : "commercial",
    235    : "commercial",
    236    : "commercial",
    251    : "commercial",
    252    : "commercial",
    253    : "commercial",
    300    : "retail",
    301    : "retail",
    302    : "retail",
    303    : "retail",
    304    : "retail",
    305    : "retail",
    306    : "retail",
    307    : "retail",
    308    : "retail",
    309    : "retail",
    310    : "retail",
    311    : "retail",
    312    : "retail",
    313    : "retail",
    314    : "retail",
    315    : "retail",
    320    : "retail",
    321    : "retail",
    322    : "retail",
    330    : "commercial",
    331    : "commercial",
    332    : "commercial",
    333    : "commercial",
    334    : "commercial",
    335    : "commercial",
    336    : "commercial",
    340    : "commercial",
    341    : "commercial",
    342    : "commercial",
    343    : "commercial",
    344    : "garage",
    345    : "garage",
    346    : "commercial",
    347    : "commercial",
    350    : "parking",
    351    : "commercial",
    352    : "parking",
    353    : "parking",
    354    : "commercial",
    360    : "municipal",
    361    : "municipal",
    362    : "municipal",
    363    : "municipal",
    364    : "municipal",
    365    : "municipal",
    370    : "commercial",
    371    : "commercial",
    372    : "commercial",
    373    : "commercial",
    374    : "commercial",
    375    : "commercial",
    376    : "commercial",
    377    : "commercial",
    378    : "commercial",
    379    : "commercial",
    380    : "commercial",
    381    : "commercial",
    382    : "commercial",
    383    : "commercial",
    384    : "commercial",
    385    : "commercial",
    386    : "commercial",
    387    : "commercial",
    388    : "commercial",
    389    : "commercial",
    390    : "commercial",
    391    : "commercial",
    399    : "commercial",
    400    : "religion",
    410    : "cemetery",
    411    : "religion",
    420    : "municipal",
    421    : "municipal",
    430    : "municipal",
    431    : "municipal",
    432    : "municipal",
    433    : "municipal",
    434    : "municipal",
    435    : "municipal",
    436    : "military",
    470    : "educational",
    471    : "educational",
    472    : "educational",
    473    : "educational",
    474    : "educational",
    475    : "educational",
    476    : "educational",
    477    : "educational",
    478    : "educational",
    479    : "educational",
    480    : "educational",
    481    : "educational",
    482    : "educational",
    483    : "educational",
    510    : "residential",
    511    : "recreation_ground",
    512    : "residential",
    513    : "residential",
    520    : "residential",
    521    : "residential",
    522    : "residential",
    523    : "residential",
    524    : "residential",
    525    : "residential",
    530    : "residential",
    531    : "residential",
    532    : "residential",
    533    : "residential",
    599    : "residential",
    600    : "residential",
    601    : "residential",
    602    : "residential",
    603    : "residential",
    604    : "residential",
    605    : "residential",
    610    : "residential",
    611    : "residential",
    612    : "residential",
    613    : "residential",
    620    : "residential",
    621    : "residential",
    622    : "residential",
    623    : "residential",
    630    : "residential",
    631    : "residential",
    640    : "residential",
    641    : "residential",
    642    : "residential",
    643    : "residential",
    650    : "recreation_ground",
    701    : "farm",
    702    : "farm",
    710    : "farm",
    711    : "farm",
    712    : "farm",
    713    : "farm",
    714    : "farm",
    720    : "farm",
    721    : "vineyard",
    722    : "vineyard",
    730    : "farm",
    731    : "farm",
    732    : "farm",
    733    : "farm",
    734    : "farm",
    735    : "farm",
    736    : "farm",
    737    : "farm",
    750    : "farm",
    751    : "farm",
    752    : "farm",
    753    : "farm",
    760    : "farm",
    761    : "farm",
    762    : "farm",
    763    : "farmyard",
    764    : "farmyard",
    765    : "farmyard",
    766    : "farmyard",
    767    : "farmyard",
    768    : "farmyard",
    769    : "farmyard",
    770    : "farmyard",
    771    : "farmyard",
    772    : "farmyard",
    773    : "farmyard",
    774    : "farmyard",
    775    : "farmyard",
    776    : "farmyard",
    777    : "farmyard",
    778    : "farmyard",
    779    : "greenhouse_horticulture",
    799    : "farmyard",
    812    : "industrial",
    813    : "industrial",
    814    : "industrial",
    815    : "industrial",
    816    : "industrial",
    817    : "industrial",
    819    : "industrial",
    823    : "commercial",
    824    : "educational",
    825    : "residential",
    826    : "residential",
    827    : "farm",
    829    : "other",
    834    : "commercial",
    835    : "commercial",
    836    : "commercial",
    837    : "commercial",
    839    : "commercial",
    845    : "educational",
    846    : "educational",
    847    : "educational",
    849    : "educational",
    856    : "residential",
    857    : "residential",
    859    : "residential",
    867    : "residential",
    869    : "residential",
    879    : "farm",
    888    : "other",
    900    : "municipal",
    901    : "municipal",
    902    : "vacant",
    903    : "municipal",
    904    : "municipal",
    950    : "municipal",
    951    : "commercial",
    952    : "farm",
    953    : "municipal",
    999    : "other",
};
#
typeuseToLanduseDesc = {
    0    : "    Vacant Land    ",
    1    : "    Manufactured home subdivision lot    ",
    2    : "    Water well site    ",
    3    : "    Improvements ass'd associated APN    ",
    4    : "    Unimproved cemetery land    ",
    100    : "    Storage warehouse    ",
    101    : "    Distribution warehouse    ",
    102    : "    Transit warehouse (truck terminal)    ",
    103    : "    Mini-storage warehouse    ",
    104    : "    Storage building    ",
    105    : "    Lumber storage    ",
    106    : "    Storage yard    ",
    110    : "    Industrial loft    ",
    111    : "    Industrial condo    ",
    112    : "    Engineering/research lab    ",
    113    : "    Light industrial    ",
    114    : "    Heavy industrial    ",
    115    : "    Food processing    ",
    116    : "    Radio/TV transmitter facility    ",
    140    : "    Rock, sand and gravel production    ",
    141    : "    Cement production    ",
    142    : "    Oil and gas production    ",
    143    : "    Chemical production    ",
    150    : "    Mining, metals    ",
    151    : "    Mining, non-metals    ",
    152    : "    Mineral rights    ",
    153    : "    Non-active patented claim    ",
    160    : "    Electric power transmission    ",
    161    : "    Electric power plant    ",
    162    : "    Co-generation, electric    ",
    163    : "    Co-generation, solar    ",
    164    : "    Co-generation, geothermal    ",
    170    : "    Water rights    ",
    171    : "    Water distribution systems    ",
    172    : "    Private water company    ",
    173    : "    Mutual water company    ",
    174    : "    PUC water company    ",
    180    : "    Pipeline right of way    ",
    210    : "    General office    ",
    211    : "    Bank, S&L    ",
    212    : "    Office condo    ",
    230    : "    Medical office    ",
    231    : "    Dental office    ",
    232    : "    Veterinary office    ",
    233    : "    Medical condo    ",
    234    : "    Urgent care/dispensary    ",
    235    : "    Outpatient surgical center    ",
    236    : "    General hospital    ",
    251    : "    Radio/TV station (not transmitter facility)    ",
    252    : "    Computer center    ",
    253    : "    Mortuary    ",
    300    : "    Retail store    ",
    301    : "    Retail warehouse    ",
    302    : "    Discount store    ",
    303    : "    Department store    ",
    304    : "    Retail strip    ",
    305    : "    Shopping center    ",
    306    : "    Regional mall    ",
    307    : "    Commercial condo    ",
    308    : "    Barber/beauty shop    ",
    309    : "    Laundromat    ",
    310    : "    Dairy sales    ",
    311    : "    Dairy sales w/gas    ",
    312    : "    Convenience store    ",
    313    : "    Convenience store w/gas    ",
    314    : "    Market    ",
    315    : "    Supermarket    ",
    320    : "    Fast food    ",
    321    : "    Restaurant    ",
    322    : "    Bar, tavern    ",
    330    : "    Hotel    ",
    331    : "    Motel    ",
    332    : "    Bed and Breakfast    ",
    333    : "    RV park    ",
    334    : "    Convalescent hospital    ",
    335    : "    Board and care home    ",
    336    : "    Rest home    ",
    340    : "    Car lot    ",
    341    : "    Auto showroom    ",
    342    : "    Auto dealership (sales/svc)    ",
    343    : "    Service station    ",
    344    : "    Service garage    ",
    345    : "    Mini-lube garage    ",
    346    : "    Car wash, coin-op    ",
    347    : "    Car wash, automatic    ",
    350    : "    Parking lot    ",
    351    : "    Auto storage yard    ",
    352    : "    Parking structure, above ground    ",
    353    : "    Parking structure, below ground    ",
    354    : "    Auto junk yard    ",
    360    : "    Airports    ",
    361    : "    Commuter terminal    ",
    362    : "    Maintenance hangar    ",
    363    : "    Storage hangar    ",
    364    : "    T hangar    ",
    365    : "    AFB reuse    ",
    370    : "    Theater, walk in movie    ",
    371    : "    Theater, drive in movie    ",
    372    : "    Theater, live stage (auditorium)    ",
    373    : "    Ice skating rink    ",
    374    : "    Roller skating rink    ",
    375    : "    Bowling alley    ",
    376    : "    Handball/racquetball    ",
    377    : "    Indoor tennis club    ",
    378    : "    Health club    ",
    379    : "    Gymnasium    ",
    380    : "    Ski lift    ",
    381    : "    Firing range    ",
    382    : "    Sports stadium    ",
    383    : "    Equestrial arena    ",
    384    : "    Miniature golf    ",
    385    : "    Driving range    ",
    386    : "    Golf course    ",
    387    : "    County club    ",
    388    : "    Clubhouse    ",
    389    : "    Fraternal/veterans organization    ",
    390    : "    City club (eg, YMCA)    ",
    391    : "    Amusement/theme park    ",
    399    : "    Misc rec facility (not common areas)    ",
    400    : "    Church    ",
    410    : "    Cemetery    ",
    411    : "    Mausoleum    ",
    420    : "    Library    ",
    421    : "    Museum    ",
    430    : "    Government building    ",
    431    : "    Post office    ",
    432    : "    Fire station    ",
    433    : "    Jail    ",
    434    : "    Public utility building    ",
    435    : "    Sewage plant    ",
    436    : "    Armory    ",
    470    : "    Educational    ",
    471    : "    Pre-school/day care center    ",
    472    : "    Elementary school    ",
    473    : "    Secondary school    ",
    474    : "    College    ",
    475    : "    Classroom    ",
    476    : "    Lecture hall    ",
    477    : "    Science building    ",
    478    : "    Manual arts building    ",
    479    : "    Arts and crafts building    ",
    480    : "    Multipurpose building    ",
    481    : "    Physical education building    ",
    482    : "    Restroom building    ",
    483    : "    Shower building    ",
    510    : "    SFR    ",
    511    : "    Recreational cabin, non-perm, des/mtn    ",
    512    : "    Transient labor cabin    ",
    513    : "    Parsonage    ",
    520    : "    Manufactured Home, fee land    ",
    521    : "    MH accessories, fee land    ",
    522    : "    MH, in-park (leased land)    ",
    523    : "    MH accessories, in-park (leased land)    ",
    524    : "    MH, dealer inventory    ",
    525    : "    MH on fee land, in manufactured home subdivision    ",
    530    : "    Condo    ",
    531    : "    PUD    ",
    532    : "    PUD, deminimus    ",
    533    : "    Timeshare (unsold interests)    ",
    599    : "    Misc residential structure    ",
    600    : "    Two SFR    ",
    601    : "    Three SFR    ",
    602    : "    Four SFR    ",
    603    : "    Duplex    ",
    604    : "    Triplex (true or combination)    ",
    605    : "    Quad (true or combination)    ",
    610    : "    Muli-SFR, 5-14 units    ",
    611    : "    Apartment, 5-14 units    ",
    612    : "    Townhouse apartment, 5-14 units    ",
    613    : "    Senior citizen apartment, 5-14 units    ",
    620    : "    Multi-SFR, 15 units and up    ",
    621    : "    Apartment, 15 units and up    ",
    622    : "    Townhouse apartment, 15 units and up    ",
    623    : "    Senior citizen apt, 15 units and up    ",
    630    : "    Condos used as apartments    ",
    631    : "    Gov't assisted apt (HUD, 236, etc.)    ",
    640    : "    Rectory/convent    ",
    641    : "    Dormitory    ",
    642    : "    Fraternity/sorority house    ",
    643    : "    Transient labor dormitory    ",
    650    : "    Manufactured home park    ",
    701    : "    Grazing    ",
    702    : "    Irrigated pasture    ",
    710    : "    Dry farm (grain)    ",
    711    : "    Row crops    ",
    712    : "    Field crops    ",
    713    : "    Alfalfa    ",
    714    : "    Vegetables    ",
    720    : "    Vines    ",
    721    : "    Vineyard, wine    ",
    722    : "    Vineyard, raisins    ",
    730    : "    Citrus    ",
    731    : "    Valencias    ",
    732    : "    Navels    ",
    733    : "    Grapefruit    ",
    734    : "    Lemons    ",
    735    : "    Deciduous    ",
    736    : "    Apples    ",
    737    : "    Avocados    ",
    750    : "    Dairy    ",
    751    : "    Poultry    ",
    752    : "    Livestock    ",
    753    : "    Bees, worms, etc.    ",
    760    : "    Creamery    ",
    761    : "    Poultry house    ",
    762    : "    Poultry shelter    ",
    763    : "    Cattle shed    ",
    764    : "    Stable    ",
    765    : "    Sheep barn    ",
    766    : "    Hog barn    ",
    767    : "    Hog shed    ",
    768    : "    Hay shed    ",
    769    : "    Grain storage    ",
    770    : "    Corn crib    ",
    771    : "    Potato storage    ",
    772    : "    Bulk fertilizer storage    ",
    773    : "    Fruit packing barn    ",
    774    : "    Tobacco barn    ",
    775    : "    Barn    ",
    776    : "    Equipment shed    ",
    777    : "    Utility building    ",
    778    : "    Quonset building    ",
    779    : "    Greenhouse    ",
    799    : "    Miscellaneous ag building    ",
    812    : "    Industrial/Admin-Prof    ",
    813    : "    Industrial/Commercial    ",
    814    : "    Industrial/Institutional    ",
    815    : "    Industrial/Single Family Residential    ",
    816    : "    Industrial/Multi Family Residential    ",
    817    : "    Industrial/Agricultural    ",
    819    : "    Industrial/Restricted    ",
    823    : "    Admin-Prof/Commercial    ",
    824    : "    Admin-Prof/Institutional    ",
    825    : "    Admin-Prof/Single Family Residential    ",
    826    : "    Admin-Prof/Multi Family Residential    ",
    827    : "    Admin-Prof/Agricultural    ",
    829    : "    Admin-Prof/Restricted    ",
    834    : "    Commercial/Institutional    ",
    835    : "    Commercial/Single Family Residential    ",
    836    : "    Commercial/Multi Family Residential    ",
    837    : "    Commercial/Agricultural    ",
    839    : "    Commercial/Restricted    ",
    845    : "    Institutional/Single Family Residential    ",
    846    : "    Institutional/Multi Family Residential    ",
    847    : "    Institutional/Agricultural    ",
    849    : "    Institutional/Restricted    ",
    856    : "    Single Family Residential/Multi Family Residential    ",
    857    : "    Single Family Residential/Agricultural    ",
    859    : "    Single Family Residential/Restricted    ",
    867    : "    Multi Family Residential/Agricultural    ",
    869    : "    Multi Family Residential/Restricted    ",
    879    : "    Agricultural/Restricted    ",
    888    : "    Other Combinations of Uses    ",
    900    : "    Dock rights only    ",
    901    : "    Flood plain    ",
    902    : "    Permanent open space easement    ",
    903    : "    Common area, greenbelt    ",
    904    : "    Common area, recreational facilities    ",
    950    : "    Right of way easement    ",
    951    : "    Cable TV (possessory interest only)    ",
    952    : "    Taylor grazing lease    ",
    953    : "    Airport landing rights    ",
    999    : "    Check    "
};

global unmatchTypeuseCode;
global unmatchTypeuseCodeParcelCount;
unmatchTypeuseCode = {};
unmatchTypeuseCodeParcelCount = {};

# Here are a number of functions: These functions define tag mappings. The API
# For these functions is that they are passed the attributes from a feature,
# and they return a list of two-tuples which match to key/value pairs.
def apn_fld(data):
    if ('apn' in data) and (data['apn']):
        return [('apn', data['apn'])]
    return None

def city_fld(data):
    if ('city' in data) and (data['city']):
        return [('addr:city', data['city'])]
    return None        

def number_fld(data):
    if ('number' in data) and (data['number']):
        # use tag '_addr:housenumber_' instead of standard tag 'addr:housenumber'
        #     so house number won't be rendered on parcel, which looks nice and protect the privacy.
        return [('addr:housenumber', data['number'])]
    return None        

def state_fld(data):
    if ('state' in data) and (data['state']):
        return [('addr:state', data['state'])]
    return None

def streetname_fld(data):
    if ('streetname' in data) and (data['streetname']):
        if ('streettype' in data):
            return [('addr:street', data['streetname']+ ' ' +data['streettype'])]            
        else:
            return [('addr:street', data['streetname'])]
    return None

def zip_fld(data):
    if ('zip' in data) and (data['zip']):
        return [('addr:postcode', data['zip'])]
    return None

def typeuse_fld(data):
    """ translate the numeric 'TYPEUSE' code to humand readable title 
            see Racho Cucamonga city parcel accessor use codes at 
            https://docs.google.com/spreadsheet/ccc?key=0ArUViD3lI1uOdGQ5T3VjNkZRdzRBTXBFQTUtU2xxYnc&hl=en_US#gid=0 
            see for OSM tagging schema/best practice for landuse at http://wiki.openstreetmap.org/wiki/Key:landuse """
    tags = []
    
    typeuseCode = data.get('typeuse', None)
    
    if (not typeuseCode) or (typeuseCode==0): 
        return
    
    typeuseCodeKey = int(typeuseCode);
    #print(typeuseCodeKey);
    #print(typeuseToLanduse.has_key(typeuseCodeKey));
    #print(typeuseToLanduse.has_key(typeuseCode));
       
    if typeuseToLanduse.has_key(typeuseCodeKey):
        tags.append(['landuse', typeuseToLanduse.get(typeuseCodeKey)])
    else:         
        if unmatchTypeuseCode.has_key(typeuseCodeKey) is False:
            #print("unmatch typeuse code %s"%typeuseCodeKey)            
            #unmatchTypeuseCode.update({typeuseCodeKey: typeuseCodeKey})
            unmatchTypeuseCode.update({typeuseCodeKey: 0});
        else:
            unmatchTypeuseCode.update({typeuseCodeKey: unmatchTypeuseCode.get(typeuseCodeKey)+1});
            #print("unmatch typeuse code %d"%unmatchTypeuseCode.get(typeuseCodeKey));
            
        tags.append(['landuse', "other"])
        
    if typeuseToLanduseDesc.has_key(typeuseCodeKey):
        tags.append(['description:en', typeuseToLanduseDesc.get(typeuseCodeKey)])
    else:        
        if unmatchTypeuseCode.has_key(typeuseCodeKey) is False:            
            #print("unmatch typeuse code %s"%typeuseCodeKey)             
            #print("unmatch typeuse code %d"%unmatchTypeuseCodeParcelCount)
            unmatchTypeuseCode.update({typeuseCodeKey: 0});
        else:
            unmatchTypeuseCode.update({typeuseCodeKey: unmatchTypeuseCode.get(typeuseCodeKey)+1});
            #print("unmatch typeuse code %d"%unmatchTypeuseCode.get(typeuseCodeKey));
        tags.append(['description:en', ""])
        
    return tags

# The most important part of the code: define a set of key/value pairs
# to iterate over to generate keys. This is a list of two-tuples: first
# is a 'key', which is only used if the second value is a string. In
# that case, it is a map of lowercased fielnames to OSM tag names: so
# fee_owner maps to 'owner' in the OSM output.

# if the latter is callable (has a __call__; is a function), then that
# method is called, passing in a dict of feature attributes with
# lowercased key names. Those functions can then return a list of
# two-tuples to be used as tags, or nothin' to skip the tags.  


tag_mapping = [ 
    ('apn', apn_fld),  
    ('city', city_fld),
    ('number', number_fld),
    ('state', state_fld),
    ('streetname', streetname_fld),
    ('zip', zip_fld),
    ('typeuse_fld', typeuse_fld)
]       

# These tags are not exported, even with the source data; this should be
# used for tags which are usually calculated in a GIS. AREA and LEN are
# common.

boring_tags = ['city', 'number', 'state', 'streetname', 'streettype', 'zip']

# Namespace is used to prefix existing data attributes. If 'None', or 
# '--no-source' is set, then source attributes are not exported, only
# attributes in tag_mapping.

#namespace = "massgis"
namespace = None 

# Uncomment the "DONT_RUN = False" line to get started. 

DONT_RUN = True
DONT_RUN = False

# =========== DO NOT CHANGE AFTER THIS LINE. ===========================
# Below here is regular code, part of the file. This is not designed to
# be modified by users.
# ======================================================================

import sys

try:
    try:
        from osgeo import ogr
    except ImportError:
        import ogr
except ImportError:
    __doc__ += gdal_install 
    if DONT_RUN:
        print __doc__
        sys.exit(2)
    print "OGR Python Bindings not installed.\n%s" % gdal_install
    sys.exit(1)

unmatchTypeuseCodeParcelCount = 0

def close_file():
    """ Internal. Close an open file."""
    global open_file
    if not open_file.closed: 
        open_file.write("</osm>")
        open_file.close()

def start_new_file():
    """ Internal. Open a new file, closing existing file if neccesary."""
    global open_file, file_counter
    file_counter += 1
    if open_file:
        close_file()
    open_file = open("%s.%s.osm" % (file_name, file_counter), "w")
    print >> open_file, "<?xml version='1.0' encoding='UTF-8'?>"
    print >> open_file, "<osm version='0.6' generator=\"polyshp2osm\">"

def clean_attr(val):
    """Internal. Hacky way to make attribute XML safe."""
    val = str(val)
    val = val.replace("&", "&amp;").replace("'", "&quot;").replace("<", "&lt;").replace(">", "&gt;").strip()
    return val

def add_ring_way(ring): 
        """Internal. write out the 'holes' in a polygon."""
        global open_file, id_counter
        ids = []
        waysWritten = []

        previousNodePosition = 0
        for nodePosition in range(ring.GetPointCount() - 1):
                if (nodePosition > 0) and ((nodePosition + 1) % 2000 == 0):
                        # We are now writing the intermediate way
                        print >> open_file, "<way id='-%s' version=\"1\" timestamp=\"%s\">" % (id_counter, timestamp)
                        waysWritten.append(id_counter) 
                        id_counter += 1

                        # We are now writing the nodes of the wat
                        for wayNodePosition in range(previousNodePosition, nodePosition):
                            # We are readding the same node to make sure it is jointive
                            print >> open_file, "<nd ref='-%s' />" % ids[wayNodePosition]
                                
                        # We are updating the current position
                        previousNodePosition = nodePosition - 1
                        print >> open_file, "</way>"

                ids.append(id_counter)
                print >> open_file, "<node id='-%s' version=\"1\" timestamp=\"%s\" lon='%s' lat='%s' />" % (id_counter, timestamp, ring.GetX(nodePosition), ring.GetY(nodePosition)) 
                id_counter += 1

        # We now have finished writing all the nodes, let's write the way
        print >> open_file, "<way id='-%s' version=\"1\" timestamp=\"%s\">" % (id_counter, timestamp)
        waysWritten.append(id_counter) 
        id_counter += 1


        # We are now writing the nodes of the  wat
        for wayNodePosition in range(previousNodePosition, len(ids)):
            # We are readding the same node to make sure it is jointive
            print >> open_file, "<nd ref='-%s' />" % ids[wayNodePosition]
                                
        # We are closing the way now
        # To make sure that we are closing properly the polygon we are adding the first point
        print >> open_file, "<nd ref='-%s' />" % ids[0]
        print >> open_file, "</way>"

        return waysWritten

def add_tags(f):
        """Internal. Write the tags"""
        global open_file, id_counter, namespace
        
        # We are now reading the fields
        field_count = f.GetFieldCount()
        fields = {}
        for field in range(field_count):
                value = f.GetFieldAsString(field)
                name = f.GetFieldDefnRef(field).GetName()
                if name and value and name not in boring_tags:
                        print >> open_file, "<tag k='%s' v='%s' />" % (name, clean_attr(value))
                fields[name.lower()] = value
        
        tags = {}
        for tag_name, map_value in tag_mapping:
                if hasattr(map_value, '__call__'):
                        tag_values = map_value(fields)
                        if tag_values:
                                for tag in tag_values:
                                        tags[tag[0]] = tag[1]
                else:
                        if tag_name in fields:
                                tags[map_value] = fields[tag_name].title()
        
        for key, value in tags.items():
                if key and value:
                        print >> open_file, "<tag k='%s' v='%s' />" % (key, clean_attr(value))

        for name, value in fixed_tags.items():
                print >> open_file, "<tag k='%s' v='%s' />" % (name, clean_attr(value))

# We are initializing the variables that we need
open_file = None
file_name = None 
id_counter = 1
file_counter = 0
counter = 0

# We are creating a timestamp value
timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

class AppError(Exception): pass

def run(filename, slice_count=1, obj_count=50000, output_location=None,
no_source=False, start_counter=1):
        """Run the converter. Requires open_file, file_name, id_counter,
        file_counter, counter to be defined in global space; not really a very good
        singleton."""
        global id_counter, file_counter, counter, file_name, open_file, namespace

        id_counter = start_counter

        if no_source:
                namespace = None

        if output_location:
                file_name = output_location

        ds = ogr.Open(filename)
        if not ds:
                raise AppError("OGR Could not open the file %s" % filename)
        l = ds.GetLayer(0)

        max_objs_per_file = obj_count 

        extent = l.GetExtent()
        if extent[0] < -180 or extent[0] > 180 or extent[2] < -90 or extent[2] > 90:
                raise AppError("Extent does not look like degrees; are you sure it is? \n(%s, %s, %s, %s)" % (extent[0], extent[2], extent[1], extent[3]))  
        slice_width = (extent[1] - extent[0]) / slice_count

        seen = {}

        print "Running %s slices with %s base filename against shapefile %s" % (slice_count, file_name, filename)

        for i in range(slice_count): 

                l.ResetReading()
                l.SetSpatialFilterRect(extent[0] + slice_width * i, extent[2], extent[0] + (slice_width * (i + 1)), extent[3])

                start_new_file()
                f = l.GetNextFeature()
                
                obj_counter = 0
                last_obj_split = 0

                while f:
                        start_id_counter = id_counter
                        if f.GetFID() in seen:
                                f = l.GetNextFeature()
                                continue
                        
                        seen[f.GetFID()] = True             
                            
                        if (obj_counter - last_obj_split) > max_objs_per_file:
                                print "Splitting file with %s objs" % (obj_counter - last_obj_split)
                                start_new_file()
                                last_obj_split = obj_counter

                        ways = []
                        
                        geom = f.GetGeometryRef()
                        numberGeometry = geom.GetGeometryCount()
                        ring = geom.GetGeometryRef(0)
                        numberOuter = 0
                        
                        ids = []
                        tagged = 0
                        # If we have no nodes in the geometry, we just get the next structure
                        if range(ring.GetPointCount() - 1) == 0 or ring.GetPointCount() == 0:
                                print >> sys.stderr, "Degenerate ring."
                                f = l.GetNextFeature()
                                continue
                        
                        previousNodePosition = 0
                        for nodePosition in range(ring.GetPointCount() - 1):
                                if (nodePosition > 0) and ((nodePosition + 1) % 2000 == 0):
                                        # We are now writing the intermediate way
                                        print >> open_file, "<way id='-%s' version=\"1\" timestamp=\"%s\">" % (id_counter, timestamp)
                                        ways.append(id_counter) 
                                        id_counter += 1

                                        # We are now writing the nodes of the way
                                        for wayNodePosition in range(previousNodePosition, nodePosition):
                                                # We are readding the same node to make sure it is jointive
                                                print >> open_file, "<nd ref='-%s' />" % ids[wayNodePosition]
                                                
                                        # We are indicating we have an extra inner
                                        # and that we have a geometry that requires a relation
                                        numberOuter += 1
                                        numberGeometry += 1
                                        
                                        # We are closing the way now
                                        add_tags(f)
                                        print >> open_file, "</way>"
                                        
                                        # We are updating the current position
                                        previousNodePosition = nodePosition - 1

                                ids.append(id_counter)
                                print >> open_file, "<node id='-%s' version=\"1\" timestamp=\"%s\" lon='%s' lat='%s' />" % (id_counter, timestamp, ring.GetX(nodePosition), ring.GetY(nodePosition)) 
                                id_counter += 1

                        # We now have finished writing all the nodes, let's write the way
                        print >> open_file, "<way id='-%s' version=\"1\" timestamp=\"%s\">" % (id_counter, timestamp)
                        ways.append(id_counter) 
                        id_counter += 1

                        # We are now writing the nodes of the  wat
                        for wayNodePosition in range(previousNodePosition, len(ids)):
                                # We are readding the same node to make sure it is jointive
                                print >> open_file, "<nd ref='-%s' />" % ids[wayNodePosition]
                                                
                        # We are closing the way now
                        # To make sure that we are closing properly the polygon we are adding the first point
                        print >> open_file, "<nd ref='-%s' />" % ids[0]
                        
                        # We verify the tagging
                        add_tags(f)
                        numberOuter += 1
                        print >> open_file, "</way>"

                        # We are now writing the relations if we have a complex polygon
                        if numberGeometry > 1:
                                # We are writing first the inner ways
                                for i in range(1, geom.GetGeometryCount()):
                                        wayList = add_ring_way(geom.GetGeometryRef(i))
                                        for wayNumber in wayList:
                                                ways.append(wayNumber)
                                
                                # We are now writing the relation
                                print >> open_file, "<relation id='-%s' version=\"1\" timestamp=\"%s\">" % (id_counter, timestamp)
                                id_counter += 1
                                
                                # We are now printing the inner ways
                                for wayPosition in range(numberOuter):
                                        print >> open_file, '<member type="way" ref="-%s" role="outer" />' % ways[wayPosition]
                                
                                # We are now printing the outer ways
                                for way in ways[numberOuter:]:
                                    print >> open_file, '<member type="way" ref="-%s" role="inner" />' % way 
                                
                                # We are adding the tags on the relation
                                print >> open_file, "<tag k='type' v='multipolygon' />"
                                add_tags(f)
                                print >> open_file, "</relation>"    
                                
                        counter += 1
                        f = l.GetNextFeature()
                        obj_counter += (id_counter - start_id_counter)

        close_file()
        print id_counter

if __name__ == "__main__":
        if DONT_RUN:
                print __doc__
                sys.exit(2)

        from optparse import OptionParser
        parse = OptionParser(usage="%prog [args] filename.shp", version=__version__)
        parse.add_option("-s", "--slice-count", dest="slice_count", help="Number of horizontal slices of data", default=1, action="store", type="int")
        parse.add_option("-o", "--obj-count", dest="obj_count", help="Target Maximum number of objects in a single .osm file", default=50000, type="int")
        parse.add_option("-n", "--no-source", dest="no_source", help="Do not store source attributes as tags.", action="store_true", default=False)
        parse.add_option("-l", "--output-location", dest="output_location", help="base filepath for output files.", default="poly_output") 
        parse.add_option("-c", "--start-counter", dest="start_counter", help="Allow to start the program at a given counter position", default=1, type="int")

        (options, args) = parse.parse_args()
            
        if not len(args):
                print "No shapefile name given!"
                parse.print_help()
                sys.exit(3)

        kw = {}
        for key in  ('slice_count', 'obj_count', 'output_location', 'no_source', 'start_counter'):
                kw[key] = getattr(options, key)

        try:
                run(args[0], **kw)   
        except AppError, E:
                print "An error occurred: \n%s" % E 
