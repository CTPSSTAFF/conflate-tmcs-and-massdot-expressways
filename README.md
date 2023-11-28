# conflate-tmcs-and-massdot-expressways
Conflate INRIX TMCs with 'events' defined on MassDOT express highways

# Overview
This directory contains the materials related to conflating the INRIX TMCs for
express highways in the CTPS model region with the CTPS 'Towns, Political Boundaries' 
(a.k.a. 'towns_pb') layer, and the MassDOTLRSE_ feature classes for speed limit and 
number of travel lanes. 

The (almost) end product of this proces is a collection of CSV files, one per MassDOT 
'route_id.' (Recall that a MassDOT 'rotue_id' is a triple of {route_system, route_number,
route_direction}. Thus the MassDOT route_id 'I90 EB' specifies the eastbound (EB)
direction of Interstate (I) number 90.) This 'almost' end product is converted into
a single Geodatabase table, which is subsequently joined to the INRIX TMC geometry for
all the routes in question, to create the "real" final product of this proecess. 
Later, this product is joined to a table containing the calculated CMP performance
measures for each TMC - the result is what is published as the data backing the 
CMP Expres Highway Performance Dashboard.

These CSV files consist of one record per the result of 'overlaying' (i.e., UNION-ing)
the INRIX TMC feature class, the 'Towns Political Boundaries' feature class, the MassDOT
LRSE_Speed_Limit feature class, and the MassDOT_LRSE_Number_Travel_Lanes feature class.
The fields of these records are:
1.  tmc - The TMC's ID string. 
2.  tmctype - Harvested from the INRIX data. Currently unused; carried over in case it might prove useful downstream.
3.  route_id - MassDOT route_id.
4.  roadnum - Harvested from INRIX data. Indicates what in MassDOT terms is the 'route_number', 
    though in a different format.
5.  direction - Harvested from the INRIX data. Indicates what in MassDOT terms is the 'route_direction', 
    though in a different format.
6.  firstnm - Harvested from the INRIX data. According to the INRIX metadata, this field is described as 
    containing "The cross street and/or interchange associated with the internal segment of 5-digit location ID."
    In practice, we have found that the accuracy of the descriptive text contained in this field varies.
    It is being carried forward as a possible aid in populating the 'seg_begin' and 'seg_end' fields in the
    feature classes read by the CMP performance dashboards.
7.  from_meas - Starting measure (in miles) of the event.
8.  to_meas - Ending measure (in miles) of the event. 
9.  length - Length of the event (in miles); calculated as from_meas - to_meas.
10. speed_limit - Speed limit for the event. Harvested from the MassDOT LRSE_Speed_Limit feature class.
                  See note below on how this value is harvested.
11. num_lanes - Number of travel lanes for the event. Harvested from the MassDOT LRSE_Number_Travel_Lanes feature class.
                See note below on how this value is harvested.
12. towns - A "+"-delimited list of towns through which the event passes. Harvested from CTPS 'towns_pb' feature class.
            The contents of this field are "+"-delimited rather than comma-delimited because we ran into difficulties
            loading a comma-delimited field _within_ a CSV (comma-separatee-values) file into an MS Access database.
            (Final computation of the CMP performance measures is done in an MS Access database.)
            
## Re-generation of MassDOT LRSE_ feature classes
In the course of work on this project, we found that the MassDOT LRSE_ feature classes for 
Speed Limit and Number of Lanes had 'gotten out of synch' with the MassDOT LRSN routes geometry.
(The hypothesis is that the later was edited outside of the 'Roads and Highways' enviroment,
and consequently the LRSE_ feature classes had not been automatically regenerated.)
These discrepancies weren't the case for many/most routes, and thus eluded being noticed for
some time, until a close inspection of SR2 around  Crosby's Corner in Lincoln/Concord
exposed the issue. It consequently became necessary to re-generate the LRSE_Speed_Limit and
LRSE_Number_Travel_Lanes feature classes as a preiminary step before performing the actual
conflation.

## Outline of processing
Processing proceeds one MassDOT route_id at a time. The driver script for 
the conflation process is "generate_tmc_events_for_expressways.py"; it uses
a subordinate "helper" script "process_csv_file.py".

The script is passed two parameters:
(1) a MassDOT route_id, and (2) a file containing the list of TMCs to conflate
onto the route. We found that INRIX's 'route_num' 
and 'direction' attributes don't always agree with MassDOT's route_id (accounding
for differences in format); this is particuarly the case when multiple routes
are coincident. Consequently, the tool must be run with both
the MassDOT route_id parameter and a file containing a list of TMC IDs.

Processing proceeds as follows:
1. Select records from the MassDOT LRSN_Routes layer with the specified route_id
2. Select records from the INRIX TMC layer with TMC IDs "IN" the list of TMCs
   specified in the TMC list file
3. Produce a raw "TMC event table" by locating each TMC along the specified route_id;
   this process is performed "manually" in code rather than using the ESRI
   "Locate Features Along Routes" because we found that the tool does NOT
   handle locating features that are more than a very small distance from
   the specified route.
4. Produce a final "TMC event table" by sorting the output of step (3) in 
   ascending order on the from\_meas field.
5. Loate the towns_pb features along the specified route_id using the 
   ESRI "Locate Features Along Routes" tool, producing a "towns event table".
6. Overlay the "tmc events" with the "towns event table", producing an
   "overlay 1 event table."
7. Select records from the LRSN_Speed_Limit layer that are WITHIN the specfied route_id;
   then locate these features along the specified route_id, producing a "speed limit event table."
8. Overlay the "speed limit event table" with the "overlay 1 event table",
   producing an "overlay 2 event table."
9. Select records from the LRSN_Number_Lanes layer that are WITHIN the specfied route_id;
   then locate these features along the specified route_id, producing a "number of lanes event table."
10. Overlay the "number of lanes event table" with the "overlay 2" event table, 
    producing an "overlay 3" event table.
11. Perform a few tidying-up opersation (see the code for details.)
12. Sort the resulting event table in asending order on from_meas,
    and add and calculate a 'calc_len' (length) field.
13. Export the resulting table as a CSV file in the csv_intermediate directory
14. Call the "helper" script "process_csv_file.py" to post-process the CSV
    file containing the intermediate results, and generate the final CSV
    output in the csv_final directory.

## Post-processing
The "intermediate" CSV file contains 1..N records per TMC. Post-prcessing transforms 
the "intermediate" CSV file into a "final" CSV file containinig _one_ record per TMC.
Post processing performs the following opterations for each unique TMC ID in the input intermediate CSV file: 
1. generate a single "+"-delimited string of town names
2. generate a speed_limit value
3. generate a num_lanes value

### Calculation of the speed_limit field
Calculate the sum of the weighted speed_lim in each input record, where weighting is by the record's 
fraction of total TMC length.Then round to a multiple of 5 MPH. 
We take care to exclude records for which 'speed_lim' is 0 or 99:  0 indicates a place in which no 'speed_lim'
event exists; 99 is an illegal speed limit and is used by MassDOT  to indicate "no value". (MassDOT currently
frowns on the use of _NULL_ event values.)

### Calculation of the num_lanes field
Calculate the sum of the weighted num_lanes in each record, where weighting is by the record's 
fraction of total TMC length. Then round the result (using math.ceil) to an integer.

# Organization of the material in this directory
+ LRSE_Speed_Limit_events.gdb - GDB containing re-generated event tables for MassDOT LRSE_Speed_Limit
+ LRSE_Speed_Limit_FC_redux.gdb - GDB containing re-generated MassDOT LRSE_Speed_Limit feature class;
  Note that this is generated one route at a time, and the individual feature classes are combined into
  a single LRSE_Speed_Limit feature class subsequently.
+ LRSE_Number_Travel_Lanes_events.gdb - GDB containing re-generated event tables for MassDOT LRSE_Speed_Limit
+ LRSE_Number_Travel_Lanes_FC_redux.gdb - GDB containing re-generated MassDOT LRSE_Number_Travel_Lanes feature class;
  Note that this is generated one route at a time, and the individual feature classes are combined into
  a single LRSE_Number_Travel_lanes feature class subsequently.
+ tmc_event_table_template.gdb - GDB containing a single table which is used as a template for
  creating the TMC event tables for individual MassDOT route_ids
+ tmc_events.gdb - GDB containing generated TMC event tables;
  This GDB contains 2 event tables for each MassDOT route_id: (1) a table containing the "raw"
  results of locating a set of TMC features along a specified route_id, and (2) the results of
  sorting the "raw" output in ascending order on the from_meas field. The name of the "raw" table is
  given by "<route_id>\_tmc\_events\_raw"; the name of the final table is given by "<route_id>\_tmc\_events".
+ town_events.gdb - GDB containing generated "town" event tables
+ speed_limit_events.gdb - GDB containing generated "speed limit" event tables
+ num_lanes_events.gdb - GDB containing generated "number of lanes" event tables
+ overlay_1.gdb - GDB containing overlay of TMC and "town" event tables
+ overlay_2.gdb - GDB contaiing overlay of "overlay 1" and "speed limit" event tables
+ overlay_3.gdb - GDB containing overlay of "overlay 2" and "number of lanes" event tables
+ csv_intermediate - directory containing one CSV file per MassDOT route_id,  with "intermediate" results,
  i.e., 1..N records per TMC
+ csv_final - directory containing one CSV file per MassDOT route_id, with "final" results,
  i.e., 1 record per TMC
+ conflated_data_from_RI.gdb - _NEEDS_TO_BE_DOCUMENTED_

The following subdirectories are fossils from previous work on this processing pipeline.
They are being retained (for now) for reference purposes only:
+ output_prep.gdb 
+ tmcs_from_sde.gdb
+ unit_test.gdb
+ misc.gdb

## Usage summary: generate_tmc_events_for_expressways.py
Usage: generate_tmc_events_for_expressways MassDOT_route_id TMC_list_file
  1. MassDOT_route_id is required
  2. list_of_tmcs_file is required
  
Files containing lists of TMCs for the express highway routes in the MPO area (and for all interstate routes state-wide)may be found in the directory:  
__\\lilliput\groups\Traffic_and_Design\11123 CMP 2019 INRIX\TMC_lists\expressways\quoted__  
The names of the files in this directory are self-explanatory, e.g., __i_90_eb_tmcs.txt__ contains the list of TMCs for I-90 Eastbound.

This script does the following:
  1. For a given MassDOT "route", generate an intermediate CSV file
     containing the "overlay" of the following events onto it:
      1. INRIX TMCs
      2. Towns
      3. Speed Limit
      4. Number of travel lanes
  2. Process the CSV file generated from step (1), producing a final output
     CSV file containing one record per TMC. 
     
Step (2) is performed by a subordinate script, process_csv_file.py
Note that process_csv_file.py depends upon the following modules:
  1. csv
  2. math
  3. pydash
  4. ma_towns

The first two are standard modules, part of any standard Python installation.
The third, pydash", requires explicit installation.
We include an explicit "try: import pydash..." at the beginning of this module, 
in order to notify the user if this library is not installed, and then exit.
The fourth resides in the same directory as this script and process_csv_file.py.

# Colophon
This repository work documents conflation work done during the last monhts of 2019 and the first months of 2020.  
Author: Ben Krepp (bkrepp@ctps.org)  
