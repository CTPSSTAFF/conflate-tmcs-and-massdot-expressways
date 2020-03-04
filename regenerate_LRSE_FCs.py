# regenerate_LRSE_FCs.py - script to re-generate selected LRSE feature classes from LRSN route geometry and LRSE event tables
#
# This script was written to deal with MassDOT LRSE FC's becoming out-of-sync with the LRSN route layer because of changes (edits)
# to LRSN route geometry. This was found to be the case, for example, for SR2 EB and WB in the "LRSN + LRSE" data copied from
# MassDOT on 19 December 2019.
#
# This script performs the conversion one 'route' at a time; the result are two sets of FC's, each set to be subsequently combined
# into a single FC using the 'Merge' tool.
#
# Ben Krepp, attending metaphysician
# 02/20/2020 - what a cool-looking date string, YOWSAH!

import arcpy

# Single (optional) parameter, specifying a file containing a newline-delimited list of MassDOT route_ids.  
route_list_file_name = arcpy.GetParameterAsText(0)  
if route_list_file_name != '':
    f = open(route_list_file_name, 'r')
    s = f.read()
    route_list = s.split('\n')
    for route_id in route_list:
        arcpy.AddMessage(route_id)
    # for   
else:
    route_list = [ 'I90 EB', 'I90 WB', 'I93 NB', 'I93 SB', 'I95 NB', 'I95 SB', 'I290 EB', 'I290 WB', 'I495 NB', 'I495 SB',
                   'US1 NB', 'US1 SB', 'US3 NB', 'US3 SB', 'US44 EB', 'US44 WB', 'SR2 EB', 'SR2 WB', 'SR3 NB', 'SR3 SB',
                   'SR24 NB', 'SR24 SB', 'SR140 NB', 'SR140 SB', 'SR146 NB', 'SR146 SB', 'SR213 EB', 'SR213 WB', 'N087 NB', 'N482 SB' ]
# end_if

# MassDOT LRSN_Routes - the route geometry here is assumed to be definitive
#
MASSDOT_LRSN_Routes_19Dec2019 = r'\\lindalino\users\Public\Documents\Public ArcGIS\CTPS data from database servers for ITS\SDE 10.6.sde\mpodata.mpodata.CTPS_RoadInventory_for_INRIX_2019\mpodata.mpodata.MASSDOT_LRSN_Routes_19Dec2019'

# MassDOT speed limit LRSE - geometry here may be out of sync w.r.t. LRSN_Routes; event table data is assumed to be OK.
#
LRSE_Speed_Limit = r'\\lindalino\users\Public\Documents\Public ArcGIS\CTPS data from database servers for ITS\SDE 10.6.sde\mpodata.mpodata.CTPS_RoadInventory_for_INRIX_2019\mpodata.mpodata.LRSE_Speed_Limit'

# Layer containing data selected from the above
#
Speed_Limit_Layer = "Speed_Limit_Layer"

# MassDOT number of travel lanes LRSE - geometry here may be out of sync w.r.t. LRSN_Routes; event table data is assumed to be OK.
#
LRSE_Number_Travel_Lanes = r'\\lindalino\users\Public\Documents\Public ArcGIS\CTPS data from database servers for ITS\SDE 10.6.sde\mpodata.mpodata.CTPS_RoadInventory_for_INRIX_2019\mpodata.mpodata.LRSE_Number_Travel_Lanes'
# Layer containing data selected from the above

Num_Lanes_Layer = "Num_Lanes_Layer"
               
# Path to "base directory"
base_dir = r'\\lilliput\groups\Data_Resources\conflate-tmcs-and-massdot-expressways'

# Path to GDB for event tables extracted from MassDOT LRSE Speed Limit FC
speed_limit_events_gdb = base_dir + '\\LRSE_Speed_Limit_events.gdb'

# Path to GDB for event tables extracted from MassDOT Number of Travel Lanes FC
num_lanes_events_gdb = base_dir + '\\LRSE_Number_Travel_Lanes_events.gdb'

# Path to GDB for regenerated LRSE_Speed_Limit FCs
speed_limit_gdb = base_dir + '\\LRSE_Speed_Limit_FC_redux.gdb'

# Path to GDB for regenerated LRSE_Number_Travel_Lanes FCs
num_lanes_gdb = base_dir + '\\LRSE_Number_Travel_Lanes_FC_redux.gdb'


# Layers for raw MassDOT LRSE Speed Limit FC and raw MassDOT LRSE Number of Travel Lanes FC
arcpy.MakeFeatureLayer_management(LRSE_Speed_Limit, Speed_Limit_Layer)
arcpy.MakeFeatureLayer_management(LRSE_Number_Travel_Lanes, Num_Lanes_Layer)

for route_id in route_list:
    arcpy.AddMessage("Processing " + route_id)
    
    MassDOT_route_query_string = "route_id = " + "'" + route_id + "'"   
    normalized_route_id = route_id.replace(' ', '_')    
    sl_et_name = normalized_route_id + '_sl_events'
    sl_layer_name = normalized_route_id + '_sl_layer'
    sl_fc_name = normalized_route_id + '_sl_fc'    
    nl_et_name = normalized_route_id + '_nl_events'
    nl_layer_name = normalized_route_id + '_nl_layer'
    nl_fc_name = normalized_route_id + '_nl_fc'
      
    arcpy.AddMessage('    Generating speed limit FC.')
    arcpy.SelectLayerByAttribute_management(Speed_Limit_Layer, "NEW_SELECTION", MassDOT_route_query_string)
    arcpy.TableToTable_conversion("Speed_Limit_Layer", speed_limit_events_gdb, sl_et_name)  
    arcpy.MakeRouteEventLayer_lr(MASSDOT_LRSN_Routes_19Dec2019, "route_id", 
                                 speed_limit_events_gdb + '\\' + sl_et_name, "route_id LINE from_measure to_measure", sl_layer_name)
    arcpy.CopyFeatures_management(sl_layer_name, speed_limit_gdb + '\\' + sl_fc_name)
    
    arcpy.AddMessage('    Generating number of travel lanes FC.')
    arcpy.SelectLayerByAttribute_management(Num_Lanes_Layer, "NEW_SELECTION", MassDOT_route_query_string)
    arcpy.TableToTable_conversion("Num_Lanes_Layer", num_lanes_events_gdb, nl_et_name)
    arcpy.MakeRouteEventLayer_lr(MASSDOT_LRSN_Routes_19Dec2019, "route_id", 
                                 num_lanes_events_gdb + '\\' + nl_et_name, "route_id LINE from_measure to_measure", nl_layer_name)                                   
    arcpy.CopyFeatures_management(nl_layer_name, num_lanes_gdb + '\\' + nl_fc_name )
# end_for over route_list