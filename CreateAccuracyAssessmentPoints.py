# path  - specify username (for Windows)
path = "C:\\Users\\%s\\Dropbox" % username

#numGrass = 20
totalPoints = 100

import arcpy
from arcpy import env

allsites = ["IB", "BM", "BH", "WC"]

for site in allsites:
    ###################################################
    ##   Administrivia
    ###################################################
    env.workspace = "%s\\CoverClassification\\%s" % (path, site)
    arcpy.env.overwriteOutput = True
    env.scratchWorkspace ="%s\\CoverClassification\\Scratch.gdb" % path

    ###################################################
    ##   calculate relative area and number of points
    ###################################################
    analysisPoly = "%s\\Site_%s\\VectorFiles\\%s_Analysis_Poly.shp"  % (path, site, site)
    cover1948 = "%s\\Site_%s\\Classifications\\%s_1948_Cover.shp" % (path, site, site)
    cover2009 = "%s\\Site_%s\\Classifications\\%s_2009_Cover.shp" % (path, site, site)

    ## clip to analysis polygon 
    cov48analysisArea = arcpy.Clip_analysis(cover1948, analysisPoly,"Cover_1948_AnalysisArea.shp")
    cov09analysisArea = arcpy.Clip_analysis(cover2009, analysisPoly, "Cover_2009_AnalysisArea.shp")
    ## dissolve to one polygon for each class
    cov48analysisArea = arcpy.Dissolve_management("Cover_1948_AnalysisArea.shp", "Cover_1948_AnalysisArea_Dissolved.shp", "Class_name")
    cov09analysisArea = arcpy.Dissolve_management("Cover_2009_AnalysisArea.shp", "Cover_2009_AnalysisArea_Dissolved.shp", "Class_name")

    ## add area
    cov48analysisArea = arcpy.AddField_management("Cover_1948_AnalysisArea_Dissolved.shp", "Area_m_sq", "DOUBLE")
    cov48analysisArea = arcpy.CalculateField_management("Cover_1948_AnalysisArea_Dissolved.shp","Area_m_sq","!SHAPE.AREA!","PYTHON_9.3")
    ## add area
    cov09analysisArea = arcpy.AddField_management("Cover_2009_AnalysisArea_Dissolved.shp", "Area_m_sq", "DOUBLE")
    cov09analysisArea = arcpy.CalculateField_management("Cover_2009_AnalysisArea_Dissolved.shp","Area_m_sq","!SHAPE.AREA!","PYTHON_9.3")

    ## summarize area in each class
    areas48 = arcpy.Statistics_analysis(cov48analysisArea, "summary1948.dbf", [['Area_m_sq','SUM']], 'Class_name')
    areas09 = arcpy.Statistics_analysis(cov09analysisArea, "summary2009.dbf", [['Area_m_sq','SUM']], 'Class_name')

    ###################################################
    ##                  Create random points
    ###################################################

    ##############
    ## for 1948
    ##############
    ## get the areas out of the tables
    coverTypeToArea = {}
    cursor = arcpy.da.SearchCursor(areas48, ['Class_name','SUM_Area_m'])
    for row in cursor:
        covertype,area=row
        coverTypeToArea[covertype] = area

    ## figure out the proportion of grass and of cover; then figure out number of points for each (and round it)
    coverTypeToArea["ratio"] = coverTypeToArea["Cover"]/coverTypeToArea["Grass"]
    numGrassFromRatio = round(totalPoints/ (1+ coverTypeToArea["ratio"]))
    #numCover=round(numGrass*coverTypeToArea["ratio"])
    numGrass = max (10,numGrassFromRatio)
    numCover=totalPoints - numGrass
    print "%s 1948: Grass - %d (%d), Cover - %d" % (site, numGrass, numGrassFromRatio, numCover)

    ## select by class for grass only polygons
    cov48lyr = arcpy.MakeFeatureLayer_management (cov48analysisArea, "cov48lyr")
    cov48lyr = arcpy.SelectLayerByAttribute_management ("cov48lyr", "NEW_SELECTION", " Class_name = 'Grass' ")
    ## create a feature class for grass only
    cov48lyr_Grass = arcpy.CopyFeatures_management("cov48lyr", "cov48lyr_Grass")
    ## generate random points within grass
    cov48_Grass_RandPoints = arcpy.CreateRandomPoints_management(out_path = env.workspace, out_name = "cov48_Grass_RandPts.shp", constraining_feature_class = cov48lyr_Grass, number_of_points_or_field =  numGrass, minimum_allowed_distance = "5 meters")

    ## do the same for cover
    cov48lyr = arcpy.SelectLayerByAttribute_management ("cov48lyr", "NEW_SELECTION", " Class_name = 'Cover' ")
    cov48lyr_Cover = arcpy.CopyFeatures_management("cov48lyr", "cov48lyr_Cover")
    cov48_Cover_RandPoints = arcpy.CreateRandomPoints_management(out_path = env.workspace, out_name = "cov48_Cover_RandPts.shp", constraining_feature_class = cov48lyr_Cover, number_of_points_or_field =  numCover, minimum_allowed_distance = "5 meters")

    ## add a field with assumed class 'grass' or 'cover'
    cov48_Cover_RandPoints = arcpy.AddField_management(cov48_Cover_RandPoints, "AssignCl", "TEXT")
    cursor = arcpy.UpdateCursor(cov48_Cover_RandPoints)
    for row in cursor:
        row.setValue('AssignCl','Cover')
        cursor.updateRow(row)
    cov48_Grass_RandPoints = arcpy.AddField_management(cov48_Grass_RandPoints, "AssignCl", "TEXT")
    cursor = arcpy.UpdateCursor(cov48_Grass_RandPoints)
    for row in cursor:
        row.setValue('AssignCl','Grass')
        cursor.updateRow(row)

    ## then union the two random points datasets so it's one random point
    cov_48_RandPoints = arcpy.Merge_management([cov48_Cover_RandPoints, cov48_Grass_RandPoints], "cov48randPoints%s.shp" % site)

    ## then add a field with actual class (leave it blank)
    cov_48_RandPoints = arcpy.AddField_management(cov_48_RandPoints, "ActualCl", "TEXT")

    ##############
    ## for 2009
    ##############
    ## get the areas out of the tables
    coverTypeToArea = {}
    cursor = arcpy.da.SearchCursor(areas09, ['Class_name','SUM_Area_m'])
    for row in cursor:
        covertype,area=row
        coverTypeToArea[covertype] = area

    ## figure out the proportion of grass and of cover; then figure out number of points for each (and round it)
    coverTypeToArea["ratio"] = coverTypeToArea["Cover"]/coverTypeToArea["Grass"]
    numGrassFromRatio = round(totalPoints/ (1+ coverTypeToArea["ratio"]))
    #numCover=round(numGrass*coverTypeToArea["ratio"])
    numGrass = max (10,numGrassFromRatio)
    numCover=totalPoints - numGrass
    print "%s 2009: Grass - %d (%d), Cover - %d" % (site, numGrass, numGrassFromRatio, numCover)

    ## select by class for grass only polygons
    cov09lyr = arcpy.MakeFeatureLayer_management (cov09analysisArea, "cov09lyr")
    cov09lyr = arcpy.SelectLayerByAttribute_management ("cov09lyr", "NEW_SELECTION", " Class_name = 'Grass' ")
    ## create a feature class for grass only
    cov09lyr_Grass = arcpy.CopyFeatures_management("cov09lyr", "cov09lyr_Grass")
    ## generate random points within grass
    cov09_Grass_RandPoints = arcpy.CreateRandomPoints_management(out_path = env.workspace, out_name = "cov09_Grass_RandPts.shp", constraining_feature_class = cov09lyr_Grass, number_of_points_or_field =  numGrass, minimum_allowed_distance = "5 meters")

    ## do the same for cover
    cov09lyr = arcpy.SelectLayerByAttribute_management ("cov09lyr", "NEW_SELECTION", " Class_name = 'Cover' ")
    cov09lyr_Cover = arcpy.CopyFeatures_management("cov09lyr", "cov09lyr_Cover")
    cov09_Cover_RandPoints = arcpy.CreateRandomPoints_management(out_path = env.workspace, out_name = "cov09_Cover_RandPts.shp", constraining_feature_class = cov09lyr_Cover, number_of_points_or_field =  numCover, minimum_allowed_distance = "5 meters")

    ## add a field with assumed class 'grass' or 'cover'
    cov09_Cover_RandPoints = arcpy.AddField_management(cov09_Cover_RandPoints, "AssignCl", "TEXT")
    cursor = arcpy.UpdateCursor(cov09_Cover_RandPoints)
    for row in cursor:
        row.setValue('AssignCl','Cover')
        cursor.updateRow(row)
    cov09_Grass_RandPoints = arcpy.AddField_management(cov09_Grass_RandPoints, "AssignCl", "TEXT")
    cursor = arcpy.UpdateCursor(cov09_Grass_RandPoints)
    for row in cursor:
        row.setValue('AssignCl','Grass')
        cursor.updateRow(row)

    ## then union the two random points datasets so it's one random point
    cov_09_RandPoints = arcpy.Merge_management([cov09_Cover_RandPoints, cov09_Grass_RandPoints], "cov09randPoints%s.shp" % site)

    ## then add a field with actual class (leave it blank)
    cov_09_RandPoints = arcpy.AddField_management(cov_09_RandPoints, "ActualCl", "TEXT")






