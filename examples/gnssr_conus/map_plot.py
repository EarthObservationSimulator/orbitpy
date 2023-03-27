""" This script plots the specular points (*not* the accessed grid points) over CONUS. Two options are available: 
        (1) Nominal mode: Limit plot to max 4 specular points per time step (or)
        (2) Raw mode: Plot all the specular points per time step.
"""
import os

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.img_tiles as cimgt

import pandas as pd

dir_path = os.path.dirname(os.path.realpath(__file__))
specular_acc_fl = dir_path+'/temp/CYG41886_specular_acc.csv'

#mode = 'Nominal' # choose mode
mode = 'Raw'

####### plot the specular points #######

# read in the specular points (not the grid access) data
df = pd.read_csv(specular_acc_fl, skiprows=4)
print(df.shape)
lons_raw = df['lon [deg]']
lats_raw = df['lat [deg]']

# Retain the frist 4 entries in each group, or all the entries if there are fewer than 2
df_modf = df.groupby('time index').apply(lambda x: x.head(4) if len(x) >= 4 else x).reset_index(drop=True)
print(df_modf.shape)
lons_nominal = df_modf['lon [deg]']
lats_nominal = df_modf['lat [deg]']

# create figure and axes with PlateCarree projection
fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})

# Add the Stamen terrain background with shaded relief
stamen_terrain = cimgt.Stamen('terrain-background')
ax.add_image(stamen_terrain, 6)

# add coastlines and borders to the map
ax.coastlines()
#ax.add_feature(cfeature.BORDERS)

# plot the data on the map
if mode=='Nominal':
    ax.plot(lons_nominal, lats_nominal, 'bo', transform=ccrs.PlateCarree(), markersize=1) 
elif mode=='Raw':
    ax.plot(lons_raw, lats_raw, 'ko', transform=ccrs.PlateCarree(), markersize=1)
else:
    print("choose valid mode of operation.")

# set the extent of the map
ax.set_extent([-125, -67, 24, 40])

# Show the map
plt.show()
