# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.3'
#       jupytext_version: 1.0.2
#   kernelspec:
#     display_name: Python [conda env:ic] *
#     language: python
#     name: conda-env-ic-py
# ---

import h5py
from pathlib import Path
import os
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import re


def read_hdf(path):
    hdf = h5py.File(path, "r")
    a_group_key = list(hdf.keys())[0]

    # Get the data
    data = np.array(hdf[a_group_key])
    return np.rot90(data)


path_prec = "DATA/PRECIPTACAO/"
files = os.listdir(path_prec)

file = "DATA/PRECIPTACAO/" + files[0]
file

prec = h5py.File(file, "r")
prec

# +
a_group_key = list(prec.keys())[0]

# Get the data
data = np.array(prec[a_group_key])
# -

data.shape

plt.imshow(data,cmap="terrain")

# Esse dados estao entre a longitude -180 e 180 e latitude 50 , - 50 (ESSA ORDEM E IMPORTANTE) com resolucao de 0.5

lon = np.arange(-180,180,0.25)
lat = np.arange(50,-50,-.25)

# Vou girar os dados em 90 graus

data = np.rot90(data)

plt.pcolormesh(lon,lat,data,cmap="terrain");

shapefile_path = "DATA/cerrado/shape.shp"
cerrado_shp = gpd.read_file(shapefile_path)
cerrado_shp.plot()

# +
fig,ax = plt.subplots(1,1)

ax.pcolormesh(lon,lat,data,cmap="terrain")
cerrado_shp.plot(ax=ax,cmap='gray');
# -

poly_cerrado = cerrado_shp.iloc[0]["geometry"]

# +
mask = np.full_like(data,True,dtype=bool)

for lat_index in range(mask.shape[0]):
    for lon_index in range(mask.shape[1]):
        point = Point(lon[lon_index],lat[lat_index])
        
        if point.within(poly_cerrado):
            # all points insinde the polygon are marked to False (in the np masked logic = No invalid)
            mask[lat_index,lon_index] = False
# -

plt.imshow(mask)

masked_data = np.ma.masked_array(data,mask)
plt.imshow(masked_data,cmap="terrain")
plt.colorbar();

month = np.full_like(data,0)


r = re.compile("3B42.199805")
iter_199805 = filter(r.match,files)

for file in iter_199805:
    data = read_hdf(path_prec + file)
    masked_data = np.ma.MaskedArray(data,mask)
    month = month + masked_data

masked_data = np.ma.masked_array(data,mask)
plt.figure(figsize=(10,10))
plt.pco(month,cmap="terrain")
plt.colorbar();


