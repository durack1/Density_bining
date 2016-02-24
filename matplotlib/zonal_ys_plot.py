#!/bin/env python
# -*- coding: utf-8 -*-
"""
Python matplotlib 
Make density/latitude section for Atl/Pac/Ind for a number of variables

(c) Eric Guilyardi Feb 2016

TODO: - add arguments for variable and output type
      - read unit from file
      - add mesh/dots for agreement zone

"""
import numpy as np
from   netCDF4 import Dataset as open_ncfile
import matplotlib as mpl
from   mpl_toolkits.basemap import Basemap, cm
from   mpl_toolkits.axes_grid1 import Grid
import matplotlib.pyplot as plt
from   matplotlib.colors import LinearSegmentedColormap

from   densitlib import zon_2dom, defVar

# -------------------------------------------------------------------------------
#                               Define work
# -------------------------------------------------------------------------------

indir = '/Users/ericg/Projets/Density_bining/'
work = 'Prod_density_april15/mme_hist/'
indir = indir+work
file2d  = 'cmip5.multimodel.historical.ensm.an.ocn.Omon.density_zon2D.nc'
file1d  = 'cmip5.multimodel.historical.ensm.an.ocn.Omon.density_zon1D.nc'


# Model agreement level
agreelev = 0.6

# Define variable  TODO: read as argument
varname = defVar('salinity')
varname = defVar('temp')
#varname = defVar('depth')
#varname = defVar('volume')
#varname = defVar('persist')

# Define plot name
plotName = 'cmip5_mme_hist_r1i1p1_'+varname['var']

# years for difference
y11 = 140-1
y12 = 146-1
y21 = 2-1
y22 = 30-1
labBowl = ['<1950','2000']

# density domain
domrho = [21.,26.,28.]   # min/mid/max
delrho = [.5,.2]
#
# -------------------------------------------------------------------------------

#-- Define variable properties

var    = varname['var']
minmax = varname['minmax']
clevsm = varname['clevsm']
legVar = varname['legVar']
unit = varname['unit']

#-- Open netcdf files
nc1d = open_ncfile(indir+'/'+file1d)
nc2d = open_ncfile(indir+'/'+file2d)

#-- Read variables
# Restrict variables to bowl
tvara = nc2d.variables[var+'Bowl'][:,1,:,:].squeeze()
tvarp = nc2d.variables[var+'Bowl'][:,2,:,:].squeeze()
tvari = nc2d.variables[var+'Bowl'][:,3,:,:].squeeze()
lev = nc2d.variables['lev'][:]
lat = nc2d.variables['latitude'][:]
# Read model agreement variables
tvaraa = nc2d.variables[var+'Agree'][:,1,:,:].squeeze()
tvarap = nc2d.variables[var+'Agree'][:,2,:,:].squeeze()
tvarai = nc2d.variables[var+'Agree'][:,3,:,:].squeeze()
# Read lightest density of persistent ocean (ptopsigma)
ptopsiga = nc1d.variables['ptopsigma'][:,1,:].squeeze()
ptopsigp = nc1d.variables['ptopsigma'][:,2,:].squeeze()
ptopsigi = nc1d.variables['ptopsigma'][:,3,:].squeeze()

#-- Build plot variables
# difference
vara = np.ma.average(tvara[y11:y12], axis=0)-np.ma.average(tvara[y21:y22], axis=0)
varp = np.ma.average(tvarp[y11:y12], axis=0)-np.ma.average(tvarp[y21:y22], axis=0)
vari = np.ma.average(tvari[y11:y12], axis=0)-np.ma.average(tvari[y21:y22], axis=0)
# mean
varam = np.ma.average(tvara, axis=0)
varpm = np.ma.average(tvarp, axis=0)
varim = np.ma.average(tvari, axis=0)
# Average model agreement over final period
varaa = np.ma.average(tvaraa[y11:y12], axis=0)
varap = np.ma.average(tvarap[y11:y12], axis=0)
varai = np.ma.average(tvarai[y11:y12], axis=0)
# Periods ptopsigma
ptopsigyr1a = np.ma.average(ptopsiga[y11:y12], axis=0)
ptopsigyr1p = np.ma.average(ptopsigp[y11:y12], axis=0)
ptopsigyr1i = np.ma.average(ptopsigi[y11:y12], axis=0)
ptopsigyr2a = np.ma.average(ptopsiga[y21:y22], axis=0)
ptopsigyr2p = np.ma.average(ptopsigp[y21:y22], axis=0)
ptopsigyr2i = np.ma.average(ptopsigi[y21:y22], axis=0)

#-- Create variable bundles
varAtl = {'name': 'Atlantic','diffBowl': vara, 'meanBowl': varam, 'agree': varaa}
varPac = {'name': 'Pacific','diffBowl': varp, 'meanBowl': varpm, 'agree': varap}
varInd = {'name': 'Indian','diffBowl': vari, 'meanBowl': varim, 'agree': varai}
vartsiga = {'yr1': ptopsigyr1a, 'yr2': ptopsigyr2a}
vartsigp = {'yr1': ptopsigyr1p, 'yr2': ptopsigyr2p}
vartsigi = {'yr1': ptopsigyr1i, 'yr2': ptopsigyr2i}
 
#-- Create figure and axes instances
fig, axes = plt.subplots(nrows=2,ncols=3,figsize=(17,5))

#-- color map
#fileGMT='palet_diff_6'
#cdict = gmtColormap(fileGMT,GMTPath = '/Users/ericg/POST_IT/config/palettes')
#cmap = LinearSegmentedColormap('campgmt',cdict)
cmap = plt.get_cmap('bwr') # red/white/blue difference map

#
# -------- Make plot ----------------
#
cnplot=zon_2dom(plt,axes[0,0],axes[1,0],lat,lev,varAtl,vartsiga,unit,minmax,clevsm,cmap,domrho,agreelev,True,'F',labBowl)

cnplot=zon_2dom(plt,axes[0,1],axes[1,1],lat,lev,varPac,vartsigp,unit,minmax,clevsm,cmap,domrho,agreelev,True,'T',labBowl)

cnplot=zon_2dom(plt,axes[0,2],axes[1,2],lat,lev,varInd,vartsigi,unit,minmax,clevsm,cmap,domrho,agreelev,True,'R',labBowl)

plt.subplots_adjust(hspace = .00001, wspace=0.05, left=0.04, right=0.86)

#-- Add colorbar
cbar = fig.colorbar(cnplot[0], ax=axes.ravel().tolist(),fraction=0.015, shrink=2.0,pad=0.05)
cbar.set_label(unit)

# add Title text
ttxt = fig.suptitle(legVar+' for '+work, fontsize=14, fontweight='bold')

#-- Output  # TODO read as argument

#plt.show()
plt.savefig(plotName+'.pdf', bbox_inches='tight')
