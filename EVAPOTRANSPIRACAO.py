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
#     display_name: Python [conda env:newic]
#     language: python
#     name: conda-env-newic-py
# ---

# # Evapotranspiracao

# +
import os
import numpy as np
import pandas as pd
import geopandas as gpd

import rasterio as rio
from rasterio.plot import show
import fiona
from rasterio.mask import mask
from rasterio.plot import plotting_extent
from shapely.geometry import mapping

import matplotlib.pyplot as plt

NODATA = -1
# -

# Verificando as pastas de evapotraspiracao

# +
path = "DATA/evapotranspiracao"
folders = os.listdir(path)
path_test = path+"/"+ folders[0] #para apenas 2000
print(folders)

files = os.listdir(path_test)
print(files)
# -

# Lendo o primeiro arquivo da primeira pasta (como teste); 

# +
path_file = path_test + "/" + files[0]
with rio.open(path_file) as src:
    map_im = src.read(masked = True)[0]
    extent = rio.plot.plotting_extent(src)
    soap_profile = src.profile

fig, ax = plt.subplots(figsize = (10,10))

ax.imshow(map_im, 
          cmap='terrain', 
          extent=extent);
# -

# Lendo o arquivo shape, Vamos usar ele para cortar a imagem acima

shape_path = "DATA/cerrado/shape.shp"
cerrado_sh = gpd.read_file(shape_path)
cerrado_sh.plot()

# Conferindo se os mesmo pertencem a mesmo sistema de referencia coordenadas (CRS -  coordinate reference system)

print('crop extent crs: ', cerrado_sh.crs)
print('lidar crs: ', soap_profile["crs"])

fig, ax = plt.subplots(figsize = (10,10))
ax.imshow(map_im, 
          cmap='terrain', 
          extent=extent
         )
cerrado_sh.plot(ax=ax, alpha=.6, color='g');

# +

extent_geojson = mapping(cerrado_sh.geometry[0])
extent_geojson

# +
with rio.open(path_file) as src:
    cerrado_crop, cerrado_crop_affine  = mask(src, [extent_geojson],
                                                        crop=True,
                                            nodata=NODATA)
    
    
cerrado_extent = plotting_extent( cerrado_crop[0],cerrado_crop_affine)
# -

cerrado_crop

# Tranformo o array acima em um masked array, para conseguir printar sem os NODATAS

cerrado_masked = np.ma.masked_where(cerrado_crop[0] == NODATA , cerrado_crop[0])

cerrado_masked

# +
plt.figure(figsize=(10,10))
plt.imshow(cerrado_masked,
           cmap="terrain",
          extent=cerrado_extent)

plt.colorbar();
# -

cerrado_masked.max()

cerrado_masked.min()


def cut_tiff(path_file,mapped_shapefile,):
    with rio.open(path_file) as src:
        crop, crop_affine  = mask(src, [mapped_shapefile],
                                crop=True,
                                nodata=NODATA)
    
    
    crop_extent = plotting_extent( crop[0],crop_affine)
    
    
    return crop,crop_extent


cut_tiff(path_file,extent_geojson)

path_folder_out = "DATA/CERRADO_EVAPOTRANSPIRACAO/"

# All meta data will be the same

cerrado_crop.shape

meta = soap_profile
meta.update({'transform': cerrado_crop_affine,
                       'height': cerrado_crop.shape[1],
                       'width': cerrado_crop.shape[2],
                       'nodata': NODATA})
meta

path_out = "DATA/cerrado_crop.tif"
with rio.open(path_out, 'w', **meta) as ff:
    ff.write(cerrado_crop[0], 1)


def save_tiff(masked_array,meta,path_out):
    with rio.open(path_out, 'w', **meta) as ff:
        ff.write(masked_array, 1)


save_tiff(cerrado_crop[0],meta,path_out)

# +

with rio.open(path_out) as src:
    map_im = src.read(masked = True)[0]
    extent = rio.plot.plotting_extent(src)
    soap_profile = src.profile

fig, ax = plt.subplots(figsize = (10,10))

ax.imshow(map_im, 
          cmap='terrain', 
          extent=extent);

# +
# Criando as pastas no path_folder_out
for folder in folders:
    if folder not in os.listdir(path_folder_out):
        os.mkdir(path_folder_out + "/" + folder)
        
# Criando um crop para cada arquivo        
for folder in folders:
    path_folder = path+"/"+ folder
    
    files = os.listdir(path_folder)
    for file in files:
        path_file = path_folder + "/" +  file
        crop, crop_extent = cut_tiff(path_file,extent_geojson)

        path_out = path_folder_out + "/" + folder + "/" + "CROPED_" + file
        save_tiff(crop[0],meta,path_out)

# +
year_tiffs = []

#path_croped = "DATA/CERRADO_EVAPOTRANSPIRACAO/"
#for folder in os.listdir(path_croped):
folder = "DATA/CERRADO_EVAPOTRANSPIRACAO/2000/"
files = os.listdir(folder)
for file in files:
    path_file = folder + "/" + file
    with rio.open(path_file) as src:
        map_im = src.read(masked = True)[0]
        year_tiffs.append(map_im)
        extent = rio.plot.plotting_extent(src)
        soap_profile = src.profile
        
# -

year_tiffs = np.array(year_tiffs)

year_tiffs.shape

mean_year = year_tiffs.mean(axis=0)
mean_year = np.ma.masked_where(mean_year == NODATA , mean_year)

# +
plt.figure(figsize=(10,10))
plt.imshow(mean_year,
           cmap="terrain",
          extent=cerrado_extent)

plt.colorbar();
# -


