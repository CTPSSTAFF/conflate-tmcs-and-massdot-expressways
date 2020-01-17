# Process CSV file produced by tmc_events_for_expressways.py, 
# producing an output CSV file with one record per TMC. 
# The input CSV file is expected to have been sorted on from_meas field, in ascending order.
#
# Ben Krepp 12/27/2019, 12/31/2019, 01/02/2020, 01/07/2020, 01/16/2020, 01/17/2020

import csv
import math
import pydash
import ma_towns


# load_csv: Read input CSV file and load it into a list of dicts (i.e., an array of ojbects in JS-speak)
#
# Parameters: in_csv_dir - full path of directory containing input CSV file
#             in_csv_file - name of input CSV file
# Return value: list of dicts containing records read from CSV file
# 
def load_csv(in_csv_dir, in_csv_file):
    open_fn = in_csv_dir + '\\' + in_csv_file
    retval = []
    with open(open_fn) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Convert string to numeric data type, where needed
            row['town_id'] = int(row['town_id'])
            row['speed_lim'] = int(row['speed_lim'])
            row['num_lanes'] = int(row['num_lanes'])
            row['from_meas'] = float(row['from_meas'])
            row['to_meas'] = float(row['to_meas'])
            row['calc_len'] = float(row['calc_len'])           
            retval.append(row)
        # for
     # with
    return retval
# def load_csv()

# write_csv: Write, in CSV format, list of dicts containing data to be output
#
# Parameters: out_csv_dir - full path of directory into which output CSV file is to be written
#             out_csv_file - name of output CSV file
# Return value: none
#
def write_csv(out_csv_dir, out_csv_file, output_data):
    open_fn = out_csv_dir + '\\' + out_csv_file
    # Note we have to open the CSV file in 'wb' mode on Windows in order to prevent each record being written out with and EXTRA newline.
    with open(open_fn, 'wb') as csvfile:
        fieldnames = ['tmc', 'tmctype', 'route_id', 'roadnum', 'direction', 'firstnm', \
                      'from_meas', 'to_meas', 'length', 'speed_limit', 'num_lanes', 'towns']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in output_data:
            writer.writerow({ 'tmc' : row['tmc'], 'tmctype' : row['tmctype'], 'route_id' : row['route_id'], 'roadnum' : row['roadnum'], 'direction' : row['direction'], \
                              'firstnm' : row['firstnm'], 'from_meas' : row['from_meas'], 'to_meas' : row['to_meas'], 'length' : row['length'], \
                              'speed_limit' : row['speed_limit'], 'num_lanes' : row['num_lanes'], 'towns' : row['towns'] })
        # for
    # with
# def write_csv()

# get_uniq_tmc_ids: Return list of unique TMC IDs in the given list of csv_records
#
# Parameter: csv_records - list of dicts from input CSV file
# Return value: list of unique TMC IDs in the above list
#
def get_uniq_tmc_ids(csv_records):
    tmc_lyst_map_obj = map(lambda x: x['tmc'], csv_records)
    tmc_lyst = list(tmc_lyst_map_obj)
    tmc_set = set(tmc_lyst)
    uniq_tmc_list = list(tmc_set)
    return uniq_tmc_list
# def get_uniq_tmc_ids() 

# get_uniq_town_ids: Return list of uniqe TOWN_IDs, sorted in ascending order 
#
# Parameter: list of dicts from input CSV data
# Return value: list of unique MassGIS TOWN_IDs in this list of dicts
#
def get_uniq_town_ids(rec_list):
    town_id_lyst_map_obj = map(lambda x: x['town_id'], rec_list)
    town_id_lyst = list(town_id_lyst_map_obj)
    town_id_set = set(town_id_lyst)
    uniq_town_id_list = list(town_id_set)
    return pydash.arrays.sort(uniq_town_id_list)
# def get_uniq_town_ids()

# town_ids_to_town_names: Given a sorted list of unique TONW_IDs, return a comma-separated string of town names
#
# Parameter: town_id_list - list of MassGIS TOWN_IDs
# Return value: return a comma-delimted string of the names of the towns associated with thest TOWN_IDs
#
def town_ids_to_town_names(town_id_list):
    town_names_str = ''
    town_names_str += ma_towns.ma_towns[int(town_id_list[0])]['town']
    del town_id_list[0]
    for town_id in town_id_list:
        town_names_str += ', ' + ma_towns.ma_towns[int(town_id)]['town']
    # for
    return town_names_str
# def town_ids_to_town_names()

# process_one_tmc_id: Process the records from the input CSV file for one TMC ID
#
# Parameter: rec_list - list of dicts from input CSV file for a single TMC ID
# Return value: a single dict summarizing the 1..N records for the given TMC ID
#
def process_one_tmc_id(rec_list):
    # Fields in retval: tmc, tmctype, from_meas, to_meas, length, 
    #                   route_id, roadnum, direction, firstnm, 
    #                   towns, town_ids (?), speed_limit, num_lanes
    print("Processing TMC " + rec_list[0]['tmc'] + " : " + str(len(rec_list)) + " records.")
    
    # Sort rec_list on from_meas in ascending order
    pydash.arrays.sort(rec_list,comparator=None,key=lambda x : x['from_meas'],reverse=False)
    overall_from_meas = rec_list[0]['from_meas']
    overall_to_meas = rec_list[len(rec_list)-1]['to_meas']
    
    # Prepare return value
    retval = {}
    retval['tmc'] = rec_list[0]['tmc']
    retval['tmctype'] = rec_list[0]['tmctype']
    retval['route_id'] = rec_list[0]['route_id']
    retval['roadnum'] = rec_list[0]['roadnum']
    retval['direction'] = rec_list[0]['direction']
    retval['firstnm'] = rec_list[0]['firstnm']
    
    # from_meas and to_meas
    retval['from_meas'] = overall_from_meas
    retval['to_meas'] = overall_to_meas
    
    # Total length
    total_length = pydash.collections.reduce_(rec_list, lambda total, x: total + x['calc_len'], 0.0)
    retval['length'] = total_length

    # Speed limit
    # Sum of weighted speed_lim in each record; weighting is by record's fraction of total TMC length,
    # rounded to a multiple of 5 MPH
    speed_limit = 0
    for rec in rec_list:
        partial_sl = float(rec['speed_lim']) * (rec['calc_len'] / total_length)
        speed_limit += partial_sl
    # for    
    round_to_multiple_of_5 = lambda x: 5 * round(x/5)
    retval['speed_limit'] = round_to_multiple_of_5(speed_limit)
    
    # Number of lanes
    # Sum of weighted num_lanes in each record (weighting is by record's fraction of total TMC length),
    # "rounded" (using math.ceil) to an integer
    num_lanes = 0
    for rec in rec_list:
        partial_nl = float(rec['num_lanes']) * (rec['calc_len'] / total_length)
        num_lanes += partial_nl
    # for
    num_lanes = math.ceil(num_lanes)
    retval['num_lanes'] = num_lanes
    
    # Town names
    # First, get sorted list of unique town_ids
    uniq_town_ids = get_uniq_town_ids(rec_list)
    # Then, turn this list into a nice, comma-separated string of town names
    town_names = town_ids_to_town_names(uniq_town_ids)
    retval['towns'] = '"' + town_names + '"'
    
    return retval
# def process_one_tmc_id()

# main_routine: Given an input CSV file with 1..N records per TMC ID,
#               generate an output CSV file with a single record per TMC ID.
#
# Parameters: in_csv_dir - full path of directory containing input CSV file
#             in_csv_file - name of input CSV file
#             out_csv_dir - full path of directory into which output CSV file is to be written
#             out_csv_dir - name out output CSV file
# Return value: none
#
def main_routine(in_csv_dir, in_csv_file, out_csv_dir, out_csv_file):
    # List of CSV data loaded - 1 to N records per TMC
    csv_loaded = []
    # List of processed CSV data - 1 record per TMC, ready for output
    csv_processed = []
    csv_loaded = load_csv(in_csv_dir, in_csv_file)
    # Get unique TMC IDs
    uniq_tmc_ids = get_uniq_tmc_ids(csv_loaded)
    for tmc_id in uniq_tmc_ids:
        recs_to_process = pydash.collections.filter_(csv_loaded, lambda x: x['tmc'] == tmc_id)
        output_rec = process_one_tmc_id(recs_to_process)
        csv_processed.append(output_rec)
    # for
    pydash.arrays.sort(csv_processed,comparator=None,key=lambda x : x['from_meas'],reverse=False)
    write_csv(out_csv_dir, out_csv_file, csv_processed)
# def main_routine()