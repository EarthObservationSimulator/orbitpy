""" Post process the specular coverage data into a different format, where the grid-points covered
    at each time step, and for a common source-id, are grouped toegether and written in the same line.
"""
import os
import pandas as pd
from orbitpy.coveragecalculator import filter_mid_interval_access

dir_path = os.path.dirname(os.path.realpath(__file__))
#grid_access_fl = dir_path + '/CYG41886/CYG41886_grid_acc.csv'

mid_grid_access_fl = dir_path + '/CYG41884/CYG41884_mid_grid_acc.csv'

new_acc_fl = dir_path + '/CYG41884/concatenated.csv'

#filter_mid_interval_access(inp_acc_df=None, inp_acc_fl=grid_access_fl, out_acc_fl=mid_grid_access_fl)

# read in the data
df = pd.read_csv(mid_grid_access_fl, skiprows=4)
#df = pd.read_csv(grid_access_fl, skiprows=4)

grouped = df.groupby(['time index', 'source id'])

# group by 'group1' and 'group2' columns and concatenate 'value' column
concatenated = df.groupby(['time index', 'source id'])['GP index'].apply(lambda x: ','.join(map(str, x))).reset_index()

# save as CSV with space as delimiter
concatenated.to_csv(new_acc_fl, sep=' ', index=False)
