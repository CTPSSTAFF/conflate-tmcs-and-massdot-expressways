# Process CSV file produced by generate_tmc_events.py, producing an output CSV file 
# with one record per TMC. 
# The input CSV file is expected to have been sorted on from_meas field, in ascending order.
#
# Ben Krepp 12/27/2019, 12/31/2019, 01/02/2020, 01/07/2020

import csv
import math
import pydash
import ma_towns

input_dir = "\\\\lilliput\\bkrepp\\data\\_cmp_2019_data_prep\\espressways2\\csv_intermediate"
output_dir = "\\\\lilliput\\bkrepp\\data\\_cmp_2019_data_prep\\espressways2\\csv_final"

# List of CSV data loaded - 1 to N records per TMC
csv_loaded = []
# List of processed CSV data - 1 record per TMC, ready for output
csv_processed = []

# Read input CSV file and load it into a list of dicts (i.e., an array of ojbects in JS-speak)
# Parameter: csv_fn - name of input CSV file (without preceeding path)
# Return value: list of dicts containing records read from CSV file
# 
def load_csv(csv_fn):
    open_fn = input_dir + "\\" + csv_fn
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
# def

def write_csv(csv_fn, output_data):
    open_fn = output_dir + "\\" + "processed_" + csv_fn
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
# def

# The following function is currently unused - see write_csv, above
def write_csv_raw(csv_fn, output_data):
    open_fn = output_dir + "\\" + "processed_" + csv_fn
    outfile = open(open_fn, 'w')
    outstr = 'tmc,tmctype,route_id,roadnu,direction,firstnm,from_meas,to_meas,length,speed_limit,num_lanes, towns\n'
    outfile.write(outstr)
    for row in output_data:
        outstr = row['tmc'] + ',' + row['tmctype'] + ',' + row['route_id'] + ',' + row['roadnum'] + ',' + row['direction'] + ','
        outstr += row['firstnm'] +',' + row['from_meas'] + ',' + row['to_meas'] + ',' + row['length'] + ','
        outstr += row['speed_limit'] + ',' + row['num_lanes']  + ',' + row['towns'] + '\n'
        outfile.write(outstr)
    # for
    outfile.close()
# def

# Return list of unique TMC IDs in the given list of csv_records
def get_uniq_tmc_ids(csv_records):
    tmc_lyst_map_obj = map(lambda x: x['tmc'], csv_records)
    tmc_lyst = list(tmc_lyst_map_obj)
    tmc_set = set(tmc_lyst)
    uniq_tmc_list = list(tmc_set)
    return uniq_tmc_list
# def  

# Return list of uniqe TOWN_IDs, sorted in ascending order 
def get_uniq_town_ids(rec_list):
    town_id_lyst_map_obj = map(lambda x: x['town_id'], rec_list)
    town_id_lyst = list(town_id_lyst_map_obj)
    town_id_set = set(town_id_lyst)
    uniq_town_id_list = list(town_id_set)
    return pydash.arrays.sort(uniq_town_id_list)
# def

# Given a sorted list of unique TONW_IDs, return a comma-separated string of town names
def town_ids_to_town_names(town_id_list):
    town_names_str = ''
    town_names_str += ma_towns.ma_towns[int(town_id_list[0])]['town']
    del town_id_list[0]
    for town_id in town_id_list:
        town_names_str += ', ' + ma_towns.ma_towns[int(town_id)]['town']
    # for
    return town_names_str
# def

# Process the records from the input CSV file for one TMC ID
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
# def

def main_routine(in_csv_filename):
    global csv_loaded, csv_processed
    out_csv_filename = in_csv_filename.replace('_output','_final')
    csv_loaded = []
    csv_processed = []
    csv_loaded = load_csv(in_csv_filename)
    # Get unique TMC IDs
    uniq_tmc_ids = get_uniq_tmc_ids(csv_loaded)
    for tmc_id in uniq_tmc_ids:
        recs_to_process = pydash.collections.filter_(csv_loaded, lambda x: x['tmc'] == tmc_id)
        output_rec = process_one_tmc_id(recs_to_process)
        csv_processed.append(output_rec)
    # for
    pydash.arrays.sort(csv_processed,comparator=None,key=lambda x : x['from_meas'],reverse=False)
    write_csv(out_csv_filename, csv_processed)
# def