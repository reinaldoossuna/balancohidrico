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

from netCDF4 import Dataset, num2date
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
from pathlib import Path
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point,Polygon

# Primeiro, desculpa por qualquer falta de acentuacao ou de cedilhas.
# Eu uso um teclado americano e por sanidade nao vou ficar mudando para o teclado br.

grace = Dataset("DATA/GRACE/GRCTellus.CSR.200204_201701.LND.RL05.DSTvSCS1409.nc")
scale = Dataset("DATA/GRACE/CLM4.SCALE_FACTOR.DS.G300KM.RL05.DSTvSCS1409.nc")

scale

lwe =grace["lwe_thickness"][0].filled()
lat = grace["lat"][:]
lon = grace["lon"][:]

plt.pcolormesh(lon,lat,lwe,cmap="terrain")
plt.colorbar();

shapefile_path = "DATA/cerrado/shape.shp"
cerrado_shp = gpd.read_file(shapefile_path)


polygon = cerrado_shp.iloc[0]["geometry"]
polygon

# + {"active": ""}
# Primeiro eh preciso mudar as coordenadas do shapefile,O grace tem umas coordenadas de 0 a 360 e o Brasil esta localizado entorno do long 300. enquanto esse shape file tem de -180 a 180 e o Brasil esta localizado entorno do long -50.
#
# para transforma a long do shape file basta (360 - long).

# +
x, y = polygon.exterior.xy
x =360 + np.array(x)

polygon_geom =Polygon(zip(x, y))
new_shp = gpd.GeoDataFrame(index=[0],crs=cerrado_shp.crs,geometry=[polygon_geom])
new_shp.plot()
# -

# Aqui podemos ver que as coordenas estao compativeis

# +
fig,ax = plt.subplots(1,1)

ax.pcolormesh(lon,lat,lwe,cmap="terrain")
new_shp.plot(ax=ax);
# -

polygon_corr = new_shp.iloc[0]["geometry"]
polygon_corr

# +
# I'll use masked array, so all values marked to True in the masked are considered invalid.
# ergo, all False values in the mask are true
mask = np.full_like(lwe,True,dtype=bool)

for lat_index in range(mask.shape[0]):
    for lon_index in range(mask.shape[1]):
        point = Point(lon[lon_index],lat[lat_index])
        
        if point.within(polygon_corr):
            # all points insinde the polygon are marked to False (in the np masked logic = No invalid)
            mask[lat_index,lon_index] = False
# -

plt.figure(figsize=(10,10))
plt.imshow(mask,cmap="gray");

# Pode parecer estar de cabeca pra baixo, e esta, mas os dados do grace tambem estao.

plt.imshow(lwe,cmap="terrain");

masked_lwe = np.ma.masked_array(lwe,mask)
plt.imshow(masked_lwe,cmap="terrain")
plt.colorbar();

scale_factor = scale["SCALE_FACTOR"][:]
scale_factor.mask = mask
scale_factor

# Why are you multipling the grace data for this scalar factor?
#
# Due to the sampling and post-processing of GRACE observations, surface mass variations at small spatial scales tend to be attenuated. Therefore, USERS SHOULD MULTIPLY THE GRCTellus LAND DATA BY THE PROVIDED SCALING GRID. The scaling grid is a set of scaling coefficients, one for each 1 degree bin of the land grids, and are intended to restore much of the energy removed by the destriping, gaussian, and degree 60 filters to the land grids. To use these scaling coefficients, the time series at one grid (1 degree bin) location must be multiplied by the scaling factor at the same 1 degree bin position. The netcdf file with gain factors is CLM4.SCALE_FACTOR.DS.G300KM.nc in the netcdf directory , and it must be applied to the GRACE grids in the same directory (an identical grid in ascii format can be found in the ascii directory) .
#
# https://grace.jpl.nasa.gov/data/get-data/monthly-mass-grids-land/

# +
scaled_lwe = masked_lwe * scale_factor


plt.imshow(scaled_lwe,cmap="terrain")
plt.colorbar();
# -


