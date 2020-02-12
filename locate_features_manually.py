# Prototype implementation of replacement for ESRI 'Locate Features Along Routes' tool.
# Author: Ben Krepp
# Date: 11 February 2020


# MassDOT LRSN Routes FC
routes_fc_name = 'mpodata.mpodata.MASSDOT_LRSN_Routes_19Dec2019'

# Selected route feature
route_feat_route_id_ix = 0; route_feat_shape_ix = 1
route_sc = arcpy.da.SearchCursor(routes_fc_name,['route_id', 'shape@'])
route_feat = route_sc.next()

# INRIX TMC FC
tmc_fc_name = 'mpodata.mpodata.INRIX_MASSACHUSETTS_TMC_2019'
# Names of fields (i.e., attributes) read in from the TMC FC
tmc_fc_fieldnames = ['tmc', 'tmctype','roadnum', 'firstnm', 'direction', 'shape@']
# Indices in the vector of fields (i.e., attributes) read in from the TMC FC
tmc_feat_tmc_id_ix = 0;  tmc_feat_tmctype_ix = 1; tmc_feat_roadnum_ix = 2; tmc_feat_firstnm_ix = 3; 
tmc_feat_direction_ix = 4; tmc_feat_shape_ix = 5

# Output event table name
# NOTE: This MUST exist before it is written to!
et_name = "TEST_1_events_tmc"

# Names of output event table fields
et_fieldnames = ['route_id', 'from_meas', 'to_meas', 'tmc', 'tmctype', 'roadnum', 'firstnm', 'direction']
# Indices of fields in output event table (actually, this isn't needed)
et_route_id_ix = 0; et_from_meas_ix = 1; et_to_meas_ix = 2; et_tmc_ix = 3; 
et_tmctype_ix = 4; et_roadnum_ix = 5; et_firstnm_ix = 6; et_direction_ix = 7

# "Insert" cursor for output event table
out_csr = arcpy.da.InsertCursor(et_name, et_fieldnames)

# Loop over the selected TMC features, which are to be located on the selected route feature
#
for tmc_feat in arcpy.da.SearchCursor(tmc_fc_name, tmc_fc_fieldnames):
    tmc_id = tmc_feat[tmc_feat_tmc_id_ix]

    # debug/trace
    print tmc_id + ', ' + str(from_meas) + ', ' + str(to_meas)    
    
    tmc_feat_fromPoint = tmc_feat[tmc_feat_shape_ix].firstPoint
    tmc_feat_toPoint = tmc_feat[tmc_feat_shape_ix].lastPoint

    projected_fromPtGeom = route_feat[route_feat_shape_ix].queryPointAndDistance(tmc_feat_fromPoint)
    projected_toPtGeom = route_feat[route_feat_shape_ix].queryPointAndDistance(tmc_feat_toPoint)

    from_meas = projected_fromPtGeom[0].firstPoint.M if (projected_fromPtGeom[0].firstPoint.M >= 0.0) else 0.0
    to_meas = projected_toPtGeom[0].firstPoint.M if (projected_toPtGeom[0].firstPoint.M >= 0.0) else 0.0
       
    # Do not write out zero-length events
    if (from_meas >= 0.0 and to_meas > 0.0) and (from_meas != to_meas):
        roh = [route_feat[route_feat_route_id_ix], from_meas, to_meas, 
               tmc_feat[tmc_feat_tmc_id_ix], tmc_feat[tmc_feat_tmctype_ix], 
               tmc_feat[tmc_feat_roadnum_ix], tmc_feat[tmc_feat_firstnm_ix], tmc_feat[tmc_feat_direction_ix]]   
        out_csr.insertRow(roh)
    else:
        # Zero-length event
        print 'Zero length event discarded: ' + tmc_id + ', ' + str(from_meas) + ', ' + str(to_meas)
    # if
# for tmc_feat

# The followng statement closes the insert cursor - not exactly the best choice for the API name :-(
del out_csr 
