""" Post process the specular coverage data into a different format, where the grid-points covered
    at each time step, and for a common source-id, are grouped toegether and written in the same line.

    Create directories and subdirectories and add/revise headers to the format accepted by the planner.

"""
import os, shutil
import pandas as pd
import csv
from skyfield.api import load 

dir_path = os.path.dirname(os.path.realpath(__file__))
out_dir = os.path.join(dir_path, 'results') # folder where the results have been written by 'main_script.py'

# Define mission parameters. This has to be in sync with the parameters defined in 'main_script.py'
epoch_JDUT1 = 2459062.5
epoch_Calender_date_UT1 = '20200801T000000Z'
step_size = '1.0'
gs_ids = ['HI', 'CHI', 'AUS'] # list of *ordered* ground-station ids

# define the output filenames
access_file_name = 'DDMI_' + epoch_Calender_date_UT1 + '.csv'
eclipse_file_name = 'eclipse_' + epoch_Calender_date_UT1 + '.csv'
gs_contact_file_name = ['gs1_' + epoch_Calender_date_UT1 + '.csv', 'gs2_' + epoch_Calender_date_UT1 + '.csv', 'gs3_' + epoch_Calender_date_UT1 + '.csv']

cygnss_sats = load.tle_file(dir_path+'/CYGNSS.txt')
for sat in cygnss_sats:
    sat_id = 'CYG' + str(sat.model.satnum)
    sat_dir = os.path.join(out_dir, sat_id)
    # delete and make a new directory for the particular satellite
    if os.path.exists(sat_dir):
        shutil.rmtree(sat_dir)
    os.makedirs(sat_dir)
    # make subfolders
    access_dir = os.path.join(sat_dir, 'access')
    os.makedirs(access_dir)
    eclipse_dir = os.path.join(sat_dir, 'eclipse')
    os.makedirs(eclipse_dir)
    gs_contact_dir = os.path.join(sat_dir, 'ground_contact')
    os.makedirs(gs_contact_dir)
    
    #### write the access file ####
    grid_access_fl = out_dir + '/' + sat_id + '_grid_acc.csv'
    new_acc_fl = access_dir + '/' + access_file_name
    # read in the data
    df = pd.read_csv(grid_access_fl, skiprows=4)
    grouped = df.groupby(['time index', 'source id'])
    # group by 'group1' and 'group2' columns and concatenate 'value' column
    concatenated = df.groupby(['time index', 'source id'])['GP index'].apply(lambda x: ','.join(map(str, x))).reset_index()
    # save as CSV with space as delimiter
    headers = [ ['Spacecraft with id ' + str(sat_id)],
                ['Epoch [JDUT1] is ' + str(epoch_JDUT1)],
                ['Step size [s] is ' + step_size]]
    
    with open(new_acc_fl, 'w', newline='') as file:
        writer = csv.writer(file)
        for header in headers:
            writer.writerow(header)
        concatenated.to_csv(file, sep=' ', index=False)

    #### write the eclipse files ####
    eclipse_fl = out_dir + '/' + sat_id + '_eclipse.csv'
    new_eclipse_fl = eclipse_dir + '/' + eclipse_file_name
    df = pd.read_csv(eclipse_fl, skiprows=3)
    headers = [ ['Eclipse times for Spacecraft with id ' + str(sat_id)],
                ['Epoch [JDUT1] is ' + str(epoch_JDUT1)],
                ['Step size [s] is ' + step_size]]
    with open(new_eclipse_fl, 'w', newline='') as file:
        writer = csv.writer(file)
        for header in headers:
            writer.writerow(header)
        df.to_csv(file, index=False)


    #### write the ground-station files ####
    for index, _gs_id in enumerate(gs_ids):
        gs_contact_fl = out_dir + '/' + sat_id + '_gs' + str(index+1) +'_contact.csv'
        new_gs_contact_fl = gs_contact_dir + '/' + gs_contact_file_name[index]
        df = pd.read_csv(gs_contact_fl, skiprows=3)
        headers = [ ['Contacts between Entity1 with id ' + str(sat_id) + ' and Entity2 with id ' + _gs_id],
                    ['Epoch [JDUT1] is ' + str(epoch_JDUT1)],
                    ['Step size [s] is ' + step_size]]
        with open(new_gs_contact_fl, 'w', newline='') as file:
            writer = csv.writer(file)
            for header in headers:
                writer.writerow(header)
            df.to_csv(file, index=False)


