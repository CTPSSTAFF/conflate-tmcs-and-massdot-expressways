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
4.  roadnum - Harvested from INRIX data. Indicates what in MassDOT terms is the 'route_number', though in a different format.
5.  direction - Harvested from the INRIX data. Indicates what in MassDOT terms is the 'route_direction', though in a different format.
6.  firstnm - Harvested from the INRIX data. {*** TBD: More needed here.)
7.  from_meas - Starting measure (in miles) of the event.
8.  to_meas - Ending measure (in miles) of the event. 
9.  length - Length of the event (in miles); calculated as from_meas - to_meas.
10. speed_limit - Speed limit for the event. Harvested from the MassDOT LRSE_Speed_Limit feature class.
                  See note below on how this value is harvested.
11. num_lanes - Number of travel lanes for the event. Harvested from the MassDOT LRSE_Number_Travel_Lanes feature class.
                See note below on how this value is harvested.
12. towns - List of towns ("+"-delimited) through which the event passes. Harvested from CTPS 'towns_pb' layer.




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
3. Produce a "TMC event table" by locating each TMC along the specified route_id;
   this process is performed "manually" in code rather than using the ESRI
   "Locate Features Along Routes" because we found that the tool does NOT
   handle locating features that are more than a very small distance from
   the specified route.
4. Loate the towns_pb features along the specified route_id using the 
   ESRI "Locate Features Along Routes" tool, producing a "towns event table".
5. Overlay the "tmc events" with the "towns event table", producing an
   "overlay 1 event table."
6. Select records from the LRSN_Speed_Limit layer that are WITHIN the specfied route_id;
   then locate these features along the specified route_id, producing a "speed limit event table."
7. Overlay the "speed limit event table" with the "overlay 1 event table",
   producing an "overlay 2 event table."
8. Select records from the LRSN_Number_Lanes layer that are WITHIN the specfied route_id;
   then locate these features along the specified route_id, producing a "number of lanes event table."
9. Overlay the "number of lanes event table" with the "overlay 2" event table, 
   producing an "overlay 3" event table.
10. Perform a few tidying-up opersation (see the code for details.)
11. Sort the resulting event table in asending order on from_meas,
    and add and calculate a 'calc_len' (length) field.
12. Export the resulting table as a CSV file in the csv_intermediate directory
13. Call the "helper" script "process_csv_file.py" to post-process the CSV
    file containing the intermediate results:

    
    

## Calculation of the speed_limit field

## Calculation of the num_lanes field



# Organization of the material in this directory


# Tool to conflate INRIX TMCs, 'Tonws, Political Boundaries', and MassDOT LRSE_* data for expressways.

Usage: generate_tmc_events_for_expressways MassDOT_route_id TMC_list_file
  1. MassDOT_route_id is required
  2. list_of_tmcs_file is optional 
If list_of_tmcs_file is not provided, all TMCs in the inidcated route will be processed.

This script does the following:
  1. For a given MassDOT "route", generate an intermediate CSV file
     containing the "overlay" of the following events onto it:
      a. INRIX TMCs
      b. Towns
      c. Speed Limit
      d. Number of travel lanes
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
