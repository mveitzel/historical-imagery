####################################################################
##                Create and clip DEM-derived (topographic) vars
####################################################################

# This function brings in a DEM that is much larger than the analysis area
# (and has already been aggregated at whatever scale the analysis is for)
# clips it to the area of the buffer around the analysis polygon (which is
# proportional to the scale of the analysis, e.g. 10 m analysis, 20 m buffer)
# and creates the other topographic variables (max slope, aspect and northness
# which is cosine of aspect and eastness which is sine of aspect, curvature
# including max curvature, plan (along isopleth) curvature and profile
# (perpendicular to isopleth/steepest direction of descent) curvature, and
# topographic moisture index (or topographic water index, or compound topographic
# index) - which involves the slope and the contributing area to a cell.
# outputs are by using the .save method for rasters, and are the medium-size
# rasters corresponding to the buffered polygon.
# the buffer avoids edge effects in raster calculations and ensures that there
# are values around the edges of the polygon when it's finally clipped.

def createTopoVars(sitePoly,largeDEM,bufferPoly,path,site,aggFac):

    import arcpy
    from arcpy import env
    #environment corresponds to the specific site
    env.workspace = "%s\\ChangeModeling\\%s" % (path, site)
    #allow overwriting
    arcpy.env.overwriteOutput = True
    #don't care much about this specific location, mostly here to help avoid arcGIS errors.
    env.scratchWorkspace ="%s\\ChangeModeling\\Scratch.gdb" % path

    # clip to approximate extent of poly for calculations of topo vars
    # uses the 2*scale of analysis buffer (e.g. 2*10 m or 2*40 m; buffer already created outside function)
    mediumDEM_UTM = arcpy.Clip_management(largeDEM, "#", "mediumDEM.tif",bufferPoly, "0", "ClippingGeometry")

    # calculate slope (maximum slope)
    mediumSLOPE = arcpy.Slope_3d(mediumDEM_UTM, "med_slope.tif", "DEGREE")
    print "Slope calculated"

    # calculate curvature (provides maximum curvature, plan curvature, and profile curvature)
    mediumcurvature = arcpy.Curvature_3d(mediumDEM_UTM, "med_curvature.tif","","med_curvature_prof.tif","med_curvature_plan.tif")
    print "Curvature calculated"

    # calculate aspect, northness, and eastness
    mediumAspect = arcpy.Aspect_3d(mediumDEM_UTM, "med_aspect.tif")
    mediumNorthn = arcpy.sa.Cos(arcpy.Raster(mediumAspect) * 3.14159 / 180)
    mediumEastn =  arcpy.sa.Sin(arcpy.Raster(mediumAspect) * 3.14159 / 180)
    mediumNorthn.save("med_Northn.tif")
    mediumEastn.save("med_Eastn.tif")
    print "aspect (Northness/Eastness) calculated"

    # calculate Heat Load Index (Stoddard and Hayes 2005 uses it)
    mediumHeatLoadIndex = 1 - (arcpy.sa.Cos( (arcpy.Raster(mediumAspect)-45) * 3.14159 /180 ))/2
    mediumHeatLoadIndex.save("med_HeatLoadIndex.tif")
    print "Heat Load Index calculated"

    # calculating solar radiation (insolation)
    mediumInsol = arcpy.sa.AreaSolarRadiation(mediumDEM_UTM, time_configuration = arcpy.sa.TimeWholeYear("2009"))#,out_global_radiation_raster="med_Insol.tif")
    mediumInsol.save("med_Insol.tif")
    print "Insolation calculated"

    # calculate Topographic Moisture/Wetness Index
    # how I learned to do this:
    # http://www.faculty.umb.edu/david.tenenbaum/eeos383/
    # http://www.faculty.umb.edu/david.tenenbaum/eeos383/eeos383-exercise03.pdf
    # http://www.faculty.umb.edu/david.tenenbaum/eeos383/eeos383-exercise05.pdf
    DEMfilled = arcpy.sa.Fill(mediumDEM_UTM)
    flowDir = arcpy.sa.FlowDirection(DEMfilled)
    flowAcc = arcpy.sa.FlowAccumulation(flowDir)
    contrArea = flowAcc * 10 * aggFac # multiply by cell area and divide by cell length
    medTMI = arcpy.sa.Ln( (contrArea + 1)/(arcpy.sa.Tan(arcpy.Raster(mediumSLOPE) * 3.14159 / 180) ) ) 
    medTMI.save("med_TMI.tif")
    print "TMI calculated"

    # calculating a distance to the nearest ridgeline; something like 'slope position'
    DistToRidge = arcpy.sa.FlowLength(flowDir,"UPSTREAM","")
    DistToRidge.save("med_DistToRidge.tif")
    print "Distance to Ridgeline calculated"

####################################################################
##                Create DEM grid & attach topo vars
####################################################################

# This function does two things: 1) creates a raster of unique values based
# on the extent, cellsize, location, and projection of the medium DEM from
# the previous function, makes it an integer, and turns it into a polygon dataset.
# Then it's clipped to the analysis polygon, and then extractvaluestopoints is used
# to get all the topographic variables' values for each of the centroids of those
# clipped DEM grid polygons.

def createDEMgridTopoVars (DEM,sitePoly, path, site):
    # same preamble from above
    import arcpy
    import numpy
    from arcpy import env
    env.workspace = "%s\\ChangeModeling\\%s" % (path, site)
    arcpy.env.overwriteOutput = True
    env.scratchWorkspace ="%s\\ChangeModeling\\Scratch.gdb" % path

    #---------create unique raster based on DEM raster using NumPy----------

    # get info from DEM raster
    left = float(arcpy.GetRasterProperties_management(DEM,"LEFT").getOutput(0))
    bottom = float(arcpy.GetRasterProperties_management(DEM,"BOTTOM").getOutput(0))
    cellx = float(arcpy.GetRasterProperties_management(DEM,"CELLSIZEX").getOutput(0))
    celly = float(arcpy.GetRasterProperties_management(DEM,"CELLSIZEY").getOutput(0))
    print "Raster info imported"
    # take raster into numpy to create sequential array
    tempRaster = arcpy.Raster(DEM)
    my_array = arcpy.RasterToNumPyArray(tempRaster)
    # .shape pulls the rows and cols of the raster
    rasrows, rascols = my_array.shape
    uniqueval=1
    # straight up nested for loop
    # very manual way to assign unique value to each cell
    for rowNum in xrange(rasrows):
        for colNum in xrange(rascols):
            my_array[rowNum, colNum] = uniqueval
            uniqueval+=1
    print "unique raster created"
    # bring back into arcGIS format, attach DEM's spatial reference information, and clip
    UniqueRaster = arcpy.NumPyArrayToRaster(my_array,arcpy.Point(left, bottom),cellx,celly,0)
    UniqueRaster.save("UniqueRaster.tif")
    spatial_ref = arcpy.Describe(DEM).spatialReference
    UniqueRaster = arcpy.DefineProjection_management(UniqueRaster, spatial_ref)
    print "Unique raster exported to ArcGIS"

    # then RasterToPoly to create grid shapefile
    # has to be an integer
    UniqueRaster_int = arcpy.Int_3d(UniqueRaster, "UniqueRaster_int.tif")
    DEM_gr_larger = arcpy.RasterToPolygon_conversion(UniqueRaster_int, "DEM_grid_larger.shp", "NO_SIMPLIFY", "VALUE")
    # this is where we clip it to the analysis polygon, with wiggly edges and holes and all
    # need to do it here so area calculations will be sure to use the area we are
    # confident in classifying and analyzing.
    DEM_gr = arcpy.Clip_analysis(DEM_gr_larger,sitePoly,"DEM_grid.shp")
    print "unique raster converted to poly and clipped"

    # poly to points to get centroid of each cell
    # because we've already clipped to analysis_poly, these might not be the centers
    # of the original DEM cells, but they will fall into one of the orginal DEM cells
    # and therefore will have consistent values from the topographic variable rasters
    # note that 'centroid' results in some points being outside the boundaries of the
    # clipped DEM grid poly cell, and this causes a discrepancy with the way ExportXY
    # does it - it uses "inside".  Also, for some reason this means it doesn't pick up
    # topographic variable values.  So I will just go with "Inside".
    cellCenters = arcpy.FeatureToPoint_management(DEM_gr, "CellCenters.shp", "INSIDE")
    print "cell centroids created"

    # extract values to points to get all the DEM & topo vars attached to centroids
    # pull all the values from the topographic variable rasters
    # note that at this point, the topo.var. information is associated with the CellCenters dataset (point dataset)
    inRasterList = [["mediumDEM.tif", "elev"], ["med_slope.tif", "slope"],["med_curvature.tif", "curv"],["med_curvature_prof.tif", "curv_prof"],["med_curvature_plan.tif", "curv_plan"],["med_Eastn.tif","eastn"],["med_Northn.tif","northn"], ["med_TMI.tif","tmi"],["med_Insol.tif","insol"],["med_DistToRidge.tif","distridge"],["med_HeatLoadIndex.tif","heatind"]]
    cellCenters =arcpy.sa.ExtractMultiValuesToPoints("cellCenters.shp", inRasterList, "NONE")
    print "Extracted topo vars to cell centroids"

    # calculate distance to prairie (not for WC)
    if site != "WC":
        prairie = "%s\\%s_Prairie.shp"  % (path, site)
        distToPrairie = arcpy.Near_analysis(cellCenters, prairie)
        print "Distance to Prairie Calculated"
    else:
        print "WC, no prairie"

####################################################################
##                Intersect DEM grid with cover classes
####################################################################

# This function does the legwork of summarizing/aggregating the cover
# for one of the years based on the clipped DEM grid.  First it does an
# intersection between the cover classification polygons with the clipped DEM grid
# polygon.  Then it uses a default dict to assign a value of 0 cover to each
# clipped DEM grid cell (but stores it in a separate vector until the end when
# it assigns these values to the clipped DEM grid polygon.  Then it uses a cursor
# to loop through all the intersected polygons and for every DEM grid polygon it aggregates
# (manually in the default dict vector) the area of each cover type it encounters.  There are
# default dict vectors for bareground, cover, and grass.  There is certainly a way to do this
# with a SQL statement but we couldn't figure out how to embed such a statement into an appropriate
# ArcGIS function. At the end we assign the default dict vector's values to a new column in the
# clipped DEM grid polygon.  At this point the information on area of each class is associated with the clipped
# DEM grid polygon.

def summarizeCoverOnDEMgrid (DEM_gr,year,cover,path,site):

    import arcpy
    # default dict can have a default value for each grid cell and wait to be updated
    from collections import defaultdict
    from arcpy import env
    env.workspace = "%s\\ChangeModeling\\%s" % (path, site)
    arcpy.env.overwriteOutput = True
    env.scratchWorkspace ="%s\\ChangeModeling\\Scratch.gdb" % path
    
    # make a layer file of grid cell poly
    gridlyr = arcpy.MakeFeatureLayer_management(DEM_gr, "gridlyr")
    print "%d features in cell grid" %int(arcpy.GetCount_management(gridlyr).getOutput(0))
    # make a layer file of cover features
    covlyr = arcpy.MakeFeatureLayer_management(cover, "cov%slyr" % year)
    print " %d features in classifcation polygons" % int(arcpy.GetCount_management(covlyr).getOutput(0))
    print "layer files created"

    # intersect cover with grid cell poly; defaults are fine
    print "Intersecting cell grid and classification polygons"
    inFeatures = ["gridlyr", "cov%slyr" % year]
    GridCoverIntersect = arcpy.Intersect_analysis(inFeatures, "GridCoverIntersect%s" % year)
    print "%d features in intersection" %int(arcpy.GetCount_management(GridCoverIntersect).getOutput(0))

    # Add area field
    GridCoverIntersect = arcpy.AddField_management("GridCoverIntersect%s.shp" % year, "Area_m_sq", "DOUBLE")
    GridCoverIntersect = arcpy.CalculateField_management(GridCoverIntersect,"Area_m_sq","!SHAPE.AREA!","PYTHON_9.3")
    print "area field added"

    # create default dicts, which know what to do when there isn't an FID - insert zero
    # (that's what the lambda value is here)
    cover_areas = defaultdict(lambda: 0)
    grass_areas = defaultdict(lambda: 0)
    bareground_areas = defaultdict(lambda: 0)

    # go through intersect file and aggregate areas for each cover type by grid cell FID
    # you have to tell the cursor which fields to pull. this is strictly a reading operation.
    cursor = arcpy.da.SearchCursor(GridCoverIntersect, ['FID_dem_gr','Area_m_sq', 'Class_name'])
    for row in cursor:
        fid,area,landclass=row
        if landclass == 'Cover':
            cover_areas[fid] += area
        elif landclass == 'Grass':
            grass_areas[fid] += area
        elif landclass == 'BareGround':
            bareground_areas[fid] += area
    print "area aggregated"

    # create field in gridfile to contain area of cover
    DEM_gr = arcpy.AddField_management(DEM_gr, "Cover%s" %year, "DOUBLE")
    DEM_gr = arcpy.AddField_management(DEM_gr, "Grass%s" %year, "DOUBLE")
    DEM_gr = arcpy.AddField_management(DEM_gr, "BareG%s" %year, "DOUBLE")

    # go and update the area of each cover type in the original gridfile
    # this is the point at which you assign the values from the default dicts
    # to the clipped DEM grid polygon dataset.
    cursor = arcpy.UpdateCursor(DEM_gr)
    for row in cursor:
        fid=row.getValue('FID')
        row.setValue('Cover%s' % year,cover_areas[fid])
        row.setValue('Grass%s' % year,grass_areas[fid])
        row.setValue('BareG%s' % year,bareground_areas[fid])
        cursor.updateRow(row)
    print "area appended to DEM grid poly"

###############################################################################
##                join DEM-derived vars with cover vars, UTM, & export
###############################################################################

# This function now uses a spatial join with 1) the cell centers of the clipped DEM
# grid polygons from createDEMgridTopoVars - this contains the topo variables, and 2)
# the cover class areas for the clipped DEM grid polygons, from summarizeCoverOnDEMgrid -
# which are attached to the polygon dataset itself. Then after doing the join, it adds
# the geographical coordinates of the cell centers manually to the shapefile using CalculateField.
# finally we save it as a shapefile and as a csv.  ExportXYv_stats which creates the csv
# also appends the geographic coordinates as XCoord and YCoord; currently those should be
# the same as NORTHING and EASTING which were manually created, less computer precision.
# note that the spatial join should be a no-brainer given that the cellcenters were centroids
# from the dataset we're joining it back to - there should have been no changes to the positional
# information of either dataset since the cell centers were extracted.  Only fields were added;
# extent shouldn't have changed so the centroids of DEM_gr should still be the same as they were
# when cellcenters was extracted earlier.

def joinDEMcoverExport (DEM_gr,cellCenters, site, aggregationFactor,path,sitePoly) :

    import arcpy
    from arcpy import env
    env.workspace = "%s\\ChangeModeling\\%s" % (path, site)
    arcpy.env.overwriteOutput = True
    env.scratchWorkspace ="%s\\ChangeModeling\\Scratch.gdb" % path

    # spatial join to grid poly (contains cover info) from centroids (contains DEM-derived topo vars)
    AllData = arcpy.SpatialJoin_analysis(DEM_gr, cellCenters, "AllData.shp","#","#","#","CONTAINS")
    print "Topo vars joined with cell cover"

    # explicitly add Northing and Easting of centroids
    AllData = arcpy.AddField_management(AllData, "northing", "DOUBLE")
    AllData = arcpy.CalculateField_management(AllData,"northing","!SHAPE.CENTROID.Y!","PYTHON_9.3")
    AllData = arcpy.AddField_management(AllData, "easting", "DOUBLE")
    AllData = arcpy.CalculateField_management(AllData,"easting","!SHAPE.CENTROID.X!","PYTHON_9.3")
    print "Northing/Easting added"
    arcpy.AddGeometryAttributes_management(AllData, "CENTROID;CENTROID_INSIDE")
    print "Centroids (inside and out) added"

    AllData = arcpy.AddField_management(AllData, "cell_area", "DOUBLE")
    AllData = arcpy.CalculateField_management(AllData,"cell_area","!SHAPE.AREA!","PYTHON_9.3")
    print "area field added"
    # in order to change the name from AllData, we need to convert it.  silly ArcGIS.
    AllData_final = arcpy.FeatureClassToFeatureClass_conversion(AllData,env.workspace,"AllData_%s_%s.shp" %(site,aggregationFactor))
    print "Final dataset shapefile created"

    # export as csv
    if site == "WC":
        ending = arcpy.ExportXYv_stats(AllData_final, ["Cover1948","Grass1948","BareG1948","Cover2009","Grass2009","BareG2009","elev","slope","curv","curv_plan","curv_prof","eastn","northn","tmi","northing","easting","CENTROID_X","CENTROID_Y","INSIDE_X","INSIDE_Y","cell_area","insol","distridge","heatind"], "COMMA", "AllData_%s_%s.csv" %(site,aggregationFactor), "ADD_FIELD_NAMES")
    else:
        ending = arcpy.ExportXYv_stats(AllData_final, ["Cover1948","Grass1948","BareG1948","Cover2009","Grass2009","BareG2009","elev","slope","curv","curv_plan","curv_prof","eastn","northn","tmi","northing","easting","CENTROID_X","CENTROID_Y","INSIDE_X","INSIDE_Y","cell_area","insol","distridge","heatind","NEAR_DIST"], "COMMA", "AllData_%s_%s.csv" %(site,aggregationFactor), "ADD_FIELD_NAMES")
    print "exported to csv"
    # and congratulations are definitely in order. :)
    print "Congratulations! You have made ArcGIS do stuff!"

