# conflate-tmcs-and-massdot-expressways

Tool to conflate INRIX TMCs and MassDOT LRS* data for expressways.

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
