###########################################################################################################################################################################################################################
##information :   This script automatically generates Qgis shape files from csv files. This function is prepared for QGIS Python. Click Plugins, then Python Console, and you can run the code there.
###########################################################################################################################################################################################################################

# Please configure it based on your main directory.
maindir = '....'

# QChainage plugin should be installed before using.
from qchainage import chainagetool
from qgis.core import QgsProject, QgsVectorLayer, QgsField, QgsVectorLayerJoinInfo, QgsCoordinateTransformContext, QgsVectorFileWriter
from qgis.utils import iface
from PyQt5.QtCore import QVariant


# Static data is stored in CSV file format. The first column should have an ID column so we can match them with array files.
CSVdir = maindir + 'csv_files\\'
# For each direction test that is gathered, a shape file needs to be prepared.
linesdir = maindir + 'ref_lines\\'
# The created vector files will be stored in this directory.
pointdir = maindir + 'map_files_out\\'

# The shape file from linesdir and the CSV file from CSVdir are represented by the variables pointX2Y and test_prelabel, respectively.
# One can travel from point A to point B or from point B to point A. Thus, we have a variable for direction as well.
def CSV2Vector1(test_prelabel, pointX2Y, direction):
    # Just establishing the initial value.
    divisioncount1 = 100
    
    # Loading reference shape line
    reflinename = 'Point_' + pointX2Y + '.shp'
    refline = iface.addVectorLayer(linesdir + direction + '\\' + reflinename, reflinename, "ogr")
    
    # Loading static data (CSV file)
    csvfilename = test_prelabel + 'Point' + pointX2Y + '_CPE' 
    csvfileuri = 'file:' + CSVdir + direction + '\\' + csvfilename + '.csv'
    csvfile = QgsVectorLayer(csvfileuri, "T", 'delimitedtext')
    QgsProject.instance().addMapLayer(csvfile)
    num_of_features = csvfile.featureCount()
    # updating point counts based on the size of the static table 
    divisioncount1 = num_of_features - 2
    
    if not refline:
        print("Layer failed to load!")

    # A new vector file (Geometry Point) is created by using the reference shape (Geometry LineString). Based on the sample count on the static table, a new vector file point count is generated.
    chainagetool.points_along_line(layerout='Output_name', startpoint=0, endpoint=0, distance=0, label="test", layer=refline, selected_only=False,
                                   force=False, fo_fila=False, divide=divisioncount1, decimal=2)
    
    templayer = QgsProject.instance().mapLayersByName('Output_name')
    refpoints = templayer[0]
    
    # Adding the ID column to the new vector file so we can match it with the static table.
    myField1 = QgsField('ID', QVariant.Int)
    refpoints.startEditing()
    refpoints.dataProvider().addAttributes([myField1])
    refpoints.updateFields()
    ID = refpoints.dataProvider().fieldNameIndex('ID')
    refpoints.commitChanges()
    
    count = 1
    refpoints.startEditing()
    # Fill the field ID with row number
    for f in refpoints.getFeatures():
        f[ID] = count
        refpoints.updateFeature(f)
        count += 1
    refpoints.commitChanges()

  
    # Combining the new point vector file with the static table according to the ID.
    refpoints.startEditing()
    joinObject = QgsVectorLayerJoinInfo()
    joinObject.setJoinFieldName('Index')
    joinObject.setTargetFieldName('ID')
    joinObject.setJoinLayerId(csvfile.id())
    joinObject.setUsingMemoryCache(True)
    joinObject.setJoinLayer(csvfile)
    refpoints.addJoin(joinObject)
    refpoints.commitChanges()
    
    # Saving new vector data where there is also static data.
    finalmapfile = test_prelabel + '_' + reflinename
    finalmapfiledir = pointdir + finalmapfile
    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = "ESRI Shapefile"
    QgsVectorFileWriter.writeAsVectorFormatV2(refpoints, finalmapfiledir, QgsCoordinateTransformContext(), options)
    
    QgsProject.instance().removeMapLayer(QgsProject.instance().mapLayersByName("Output_name")[0].id())
    QgsProject.instance().removeMapLayer(QgsProject.instance().mapLayersByName(reflinename)[0].id())
    QgsProject.instance().removeMapLayer(QgsProject.instance().mapLayersByName("T")[0].id())
    
    loadback = iface.addVectorLayer(finalmapfiledir, finalmapfile, "ogr")
    return 0
