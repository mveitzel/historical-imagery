
#####################
### ADMINISTRIVIA ###
#####################

# make it work for a different site (IB, BM, BH, WC)
site = "WC"
print site

# specify username
path = "C:\\Users\\%s\\Dropbox" % username

# Import system modules
import arcpy
from arcpy import env

# import MVES module with functions for spatial analysis
# see that file for details on those functions
from CoverChangeGISanalysisFunctions import *

# allow overwriting - so make sure to save results in different names
arcpy.env.overwriteOutput = True
#arcpy.SetLogHistory(True)

# set workspace
env.workspace = "%s\\ChangeModeling\\%s" % (path, site)
env.scratchWorkspace ="%s\\ChangeModeling\\Scratch.gdb" % path

# in order to use 3D analyst and Spatial Analyst
arcpy.CheckOutExtension("3D")
arcpy.CheckOutExtension("Spatial")


# paths to files
# these three files were always consistently named
cover1948 = "%s\\Site_%s\\Classifications\\%s_1948_Cover.shp" % (path, site, site)
cover2009 = "%s\\Site_%s\\Classifications\\%s_2009_Cover.shp" % (path, site, site)
ForestMask = "%s\\IntermediateClassificationProducts\\%s_Forest.shp"  % (path, site)
DEMfile = "%s\\DEMs\\n41w124\\grdn41w124_13" % path

# and the DEM tile is different for BH
if site=="BH":
    DEMfile = "%s\\Professional\\ConiferEncroachment\\DEMs\\n42w124\\grdn42w124_13" % path

# create the analysis polygon by intersecting the forest mask with the 'good registration, no garbage, no clearcut' polygon
sitep = arcpy.MakeFeatureLayer_management(sitePoly, "siteplyr")
forma = arcpy.MakeFeatureLayer_management(ForestMask, "formalyr")
inFeatures = ["siteplyr", "formalyr"]
sitePoly = arcpy.Intersect_analysis(inFeatures, "%s\\Site_%s\\VectorFiles\\%s_Analysis_Poly.shp" % (path,site,site))

largeDEM = arcpy.Raster(DEMfile)


#################
###  ANALYSIS ###
#################

# note that ArcGIS has serious issues with violating its own permissions when you do repeated
# loops as I have done here.  So you have to restart this code and start it at whatever
# aggregationFactor it failed on (also commenting out the code before the loop so you don't
# re-generate the 10-m scale data every time you have to start over, since it's the largest
# dataset.  But it does ultimately run - and sometimes you don't get any errors.
# failures are usually "AddField" or other things like that, with the 999999 error code.

aggregationFactor = 1

print "Aggregation Factor %s" % aggregationFactor
# buffer the site poly to clip the DEM for creation of topographic vars
# because the Aggregation Factor is 1 through 10, multiply by 10 for the
# size of a basic grid cell, and then by 2 to make sure you have a large enough
# buffer.
BufferSize = 20*aggregationFactor
# create the buffer.
outsidebufferPoly = arcpy.Buffer_analysis(sitePoly, "sitePoly%dBufferoutside.shp" % BufferSize,"%d Meters" % BufferSize, "OUTSIDE_ONLY","","ALL","")
# and add in the inside, too.  we don't just want the buffer.
bufferPoly = arcpy.Union_analysis([sitePoly,outsidebufferPoly],"sitePoly%dBuffer.shp" % BufferSize)
# project the raster!
largeDEM_UTM = arcpy.ProjectRaster_management(largeDEM, "largeDEM_UTM.tif", bufferPoly,"CUBIC")

# call *ALL* the functions!
createTopoVars(sitePoly,"largeDEM_UTM.tif",bufferPoly,path,site,aggregationFactor)
createDEMgridTopoVars("mediumDEM.tif",sitePoly,path, site)
summarizeCoverOnDEMgrid ("DEM_grid.shp","1948",cover1948,path,site)
summarizeCoverOnDEMgrid ("DEM_grid.shp","2009",cover2009,path,site)
joinDEMcoverExport("DEM_grid.shp","CellCenters.shp",site,aggregationFactor,path,sitePoly)

for aggregationFactor in range(2,11):
    print "Aggregation Factor %s" % aggregationFactor
    #aggregate the DEM - using the 'mean' as the way to come up with the aggregated value for the raster
    largeDEMagg = arcpy.sa.Aggregate(largeDEM_UTM, aggregationFactor, "MEAN", "TRUNCATE", "NODATA")
    largeDEMagg.save("largeDEM_UTM.img")

    # buffer the site poly to clip the DEM for creation of topographic vars
    # this code is as above.
    BufferSize = 2*10*aggregationFactor #2 times the cell size
    outsidebufferPoly = arcpy.Buffer_analysis(sitePoly, "sitePoly%dBufferoutside.shp" % BufferSize,"%d Meters" % BufferSize, "OUTSIDE_ONLY","","ALL","")
    bufferPoly = arcpy.Union_analysis([sitePoly,outsidebufferPoly],"sitePoly%dBuffer.shp" % BufferSize)
    largeDEM_UTM = arcpy.ProjectRaster_management(largeDEM, "largeDEM_UTM.tif", bufferPoly,"CUBIC")

    # this code is as above.  call *ALL* the functions!
    createTopoVars(sitePoly,largeDEMagg,bufferPoly,path,site,aggregationFactor)
    createDEMgridTopoVars("mediumDEM.tif",sitePoly,path, site)
    summarizeCoverOnDEMgrid ("DEM_grid.shp","1948",cover1948,path,site)
    summarizeCoverOnDEMgrid ("DEM_grid.shp","2009",cover2009,path,site)
    joinDEMcoverExport("DEM_grid.shp","CellCenters.shp",site,aggregationFactor,path,sitePoly)

