# conflate-tmcs-and-massdot-expressways
Conflate INRIX TMCs with 'events' defined on MassDOT express highways

# Overview
This directory contains the materials related to conflating the INRIX TMCs for
express highways in the CTPS model region with the CTPS 'Towns, Political Boundaries' 
(a.k.a. 'towns_pb') layer, and the MassDOTLRSE_ feature classes for speed limit and number of travel lanes.

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
6.  firstnm - Harvested from the INRIX data.
7.  from_meas - Starting measure (in miles) of the event.
8.  to_meas - Ending measure (in miles) of the event. 
9.  length - Length of the event (in miles); calculated as from_meas - to_meas.
10. speed_limit - Speed limit for the event. Harvested from the MassDOT LRSE_Speed_Limit feature class.
                  See note below on how this value is harvested.
11. num_lanes - Number of travel lanes for the event. Harvested from the MassDOT LRSE_Number_Travel_Lanes feature class.
                See note below on how this value is harvested.
12. towns - List of towns ("+"-delimited) through which the event passes. Harvested from CTPS 'towns_pb' layer.

## Calculation of the speed_limit field

## Calculation of the num_lanes field


## Re-generation of MassDOT LRSE_ feature classes


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
