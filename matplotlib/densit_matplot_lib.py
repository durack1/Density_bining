"""
Densitlib for matplotlib for density plots
(c) Eric Guilyardi
Feb 2016

"""

import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import MaxNLocator

def findToE(signal, noise, mult):
    '''
    define Time of Emergence (ToE) from last time index at which signal is larger than mult*noise
        signal is [time,space]
        noise is [space]
        mult is float
    '''
    timN = signal.shape[0]
    toe_wrk = np.ma.ones(signal.shape)*1. # init toe_wrk array to 1
    signaltile = np.reshape(np.tile(noise,timN),signal.shape) # repeat timN
    toe_idx = np.argwhere(abs(signal) >= mult*signaltile) # find indices of points > stdev
    toe_wrk[toe_idx[:,0],toe_idx[:,1]] = 0. # set points in toe_wrk to zero
    toe = timN-np.flipud(toe_wrk).argmax(axis=0) # compute ToE1

    return toe

# -----------------------------
#  Build zonal mean with zoom
# -----------------------------

def zon_2dom(plt, ax0, ax1, lat, lev, varBasin, varSigma, unit, minmax, clevsm, cmap, domrho, agreelev, agreeON, noax,
             labBowl):
    # -- variables
    var = varBasin['diffBowl']
    varm = varBasin['meanBowl']
    varag = varBasin['agree']

    # -- title and bowl labels
    title = varBasin['name']
    label1 = labBowl[0]
    label2 = labBowl[1]

    # -- contour levels
    rhomin = domrho[0]
    rhomid = domrho[1]
    rhomax = domrho[2]

    # -- Latmin/max
    latmin = -80.
    latmax = 80.
    deltalat = 20
    labels = ['', '60S', '40S', '20S', 'Eq', '20N', '40N', '60N', '']
    #
    # ====  Upper panel  ===================================================
    #
    ax0.axis([latmin, latmax, rhomin, rhomid])
    ax0.invert_yaxis()
    ax0.xaxis.set_ticks(np.arange(latmin, latmax, deltalat))
    ax0.set_xticklabels(labels)
    if noax == 'T':
        ax0.set_yticklabels([])
        ax1.set_yticklabels([])
    if noax == 'R':
        ax0.yaxis.tick_right()
        ax1.yaxis.tick_right()

    # -- levels for shade plot
    levels = MaxNLocator(nbins=minmax[2]).tick_values(minmax[0], minmax[1])

    # -- Format for contour labels
    levfmt='%.0f'
    if abs(clevsm[1]-clevsm[0]) < 1:
        levfmt='%.1f'
    if abs(clevsm[1]-clevsm[0]) < 0.1:
        levfmt='%.2f'

    # -- draw filled contours of period diff
    cnplot = ax0.contourf(lat, lev, var, cmap=cmap, levels=levels)

    if agreeON:
        # -- draw agreement contour > agreement level (agreelev)
        cmapbl = LinearSegmentedColormap('cmapbl', bluecol())
        chplot = ax0.contourf(lat, lev, varag, levels=[-agreelev, agreelev], hatches=['..'], colors='none')
        cpplot = ax0.contour(lat, lev, varag, [agreelev - .0001, agreelev + 0.00001], cmap=cmapbl, linewidths=2)
        cpplot = ax0.contour(lat, lev, varag, [-agreelev - .0001, -agreelev + 0.00001], cmap=cmapbl, linewidths=2)

    # -- draw mean contours
    cmapb = LinearSegmentedColormap('cmapb', blkcol())
    cpplot = ax0.contour(lat, lev, varm, clevsm, cmap=cmapb)
    ax0.clabel(cpplot, inline=1, fontsize=10, fmt=levfmt)

    # -- draw ptopsigma for 2 periods (yr1 = ref, yr2 = end of serie)
    lnplot1 = ax0.plot(lat, varSigma['yr1'], linestyle='--', color='black', linewidth=2)
    lnplot2 = ax0.plot(lat, varSigma['yr2'], linestyle='-', color='black', linewidth=2)

    #
    # ====  Lower panel   ===================================================
    #
    ax1.axis([latmin, latmax, rhomid, rhomax])
    ax1.invert_yaxis()
    ax1.xaxis.set_ticks(np.arange(latmin, latmax, deltalat))
    ax1.set_xticklabels(labels)

    # -- draw filled contours
    cnplot = ax1.contourf(lat, lev, var, cmap=cmap, levels=levels)

    if agreeON:
        # -- draw agreement contour > agreement level (agreelev)
        cmapbl = LinearSegmentedColormap('cmapbl', bluecol())
        chplot = ax1.contourf(lat, lev, varag, levels=[-agreelev, agreelev], hatches=['..'], colors='none')
        cpplot = ax1.contour(lat, lev, varag, [agreelev - .0001, agreelev + 0.00001], cmap=cmapbl, linewidths=2)
        cpplot = ax1.contour(lat, lev, varag, [-agreelev - .0001, -agreelev + 0.00001], cmap=cmapbl, linewidths=2)

    # -- draw mean contours
    cmapb = LinearSegmentedColormap('cmapb', blkcol())
    cpplot = ax1.contour(lat, lev, varm, clevsm, cmap=cmapb)
    ax1.clabel(cpplot, inline=1, fontsize=10, fmt=levfmt)

    # -- draw ptopsigma for 2 periods (yr1 = ref, yr2 = end of serie)
    lnplot1b = ax1.plot(lat, varSigma['yr1'], linestyle='--', color='black', linewidth=2, label=label1)
    lnplot2b = ax1.plot(lat, varSigma['yr2'], linestyle='-', color='black', linewidth=2, label=label2)

    # -- Add legend for bowl position
    plt.legend(loc='upper right', title='Bowl')

    # -- add plot title
    ax0.text(latmin + 10, rhomin + 1, title, fontsize=14, fontweight='bold')

    return [cnplot, lnplot1, lnplot2]


# --------------------------------
#   List variables and properties
# --------------------------------

def defVar(longName):
    salinity = {
        'longN': 'salinity',  # long name
        'var': 'isonso',  # variable name
        'minmax': [-.2, .2, 16],  # for diff shading + number of color interval
        'clevsm': np.arange(30, 40, .2),  # for mean contours
        'clevsmdif': np.arange(-.2, .2, .025),  # for mean contours
        'clevsmstd': np.arange(0., .2, .005),  # for stddev contours
        '1dminmax': [-.1, .1], # for 1D ToE plots
        'legVar': "Salinity",  # Legend name
        'unit': "PSU",  # TODO: could be read from file
    }

    temp = {'var': 'isonthetao', 'minmax': [-.4, .4, 16], 'clevsm': np.arange(-2, 30, 1),
            'clevsmstd': np.arange(0, 2., .01), '1dminmax': [-.4, .4],'clevsmdif': np.arange(-.4, .4, .05),
            'legVar': "Temperature", 'unit': "C", 'longN': 'temp',
            }
    depth = {'var': 'isondepth', 'minmax': [-75., 75., 30], 'clevsm': np.arange(0, 2000, 100),
             'clevsmstd': np.arange(0, 20, 5),'1dminmax': [-10, 50],'clevsmdif': np.arange(-75, 75, 10),
             'legVar': "Depth", 'unit': "m", 'longN': 'depth',
             }
    volume = {'var': 'isonvol', 'minmax': [-20., 20., 20], 'clevsm': np.arange(0, 200, 20),
              'clevsmstd': np.arange(0, 20, 1),'1dminmax': [-5, 5],'clevsmdif': np.arange(-20, 20, 5),
              'legVar': "Volume", 'unit': "1.e12 m^3", 'longN': 'volume',
              }
    persist = {'var': 'isonpers', 'minmax': [-10., 10., 20], 'clevsm': np.arange(0, 90, 10),
               'clevsmstd': np.arange(0, 3., .5),'1dminmax': [-50, 50],'clevsmdif': np.arange(-10, 10, 2),
               'legVar': "Persistence", 'unit': "% of time", 'longN': 'persist'
               }

    vars = [salinity, temp, depth, volume, persist]

    varout = 'None'
    for ivar in range(len(vars)):
        if vars[ivar]['longN'] == longName:
            varout = vars[ivar]

    return varout


# - def black color bar
def blkcol():
    cdict = {'red': ((0.0, 0.0, 0.0),
                     (1.0, 1.0, 1.0)),
             'green': ((0.0, 0.0, 0.0),
                       (1.0, 1.0, 1.0)),
             'blue': ((0.0, 0.0, 0.0),
                      (1.0, 1.0, 1.0))}
    return (cdict)


# - def blues color bar
def bluecol():
    cdict = {'red': ((0.0, 0.0, 0.0),
                     (1.0, 0.0, 0.0)),
             'green': ((0.0, 0.0, 0.0),
                       (1.0, 0.0, 0.0)),
             'blue': ((0.0, 0.0, 1.0),
                      (1.0, 1.0, 1.0))}
    return (cdict)

# - average in lat/rho domain

def averageDom(field, dim, domain, lat, rho):

    latidx = np.argwhere((lat >= domain[0]) & (lat <= domain[1])).transpose()
    rhoidx = np.argwhere((rho >= domain[2]) & (rho <= domain[3])).transpose()
    lidx1 = latidx[0][0];
    lidx2 = latidx[0][-1]
    ridx1 = rhoidx[0][0];
    ridx2 = rhoidx[0][-1]
    if dim == 3:
        vara = np.ma.average(field[:, ridx1:ridx2, :], axis=1)
        var_ave = np.ma.average(vara[:, lidx1:lidx2], axis=1)
    else:
        vara = np.ma.average(field[ridx1:ridx2, :], axis=0)
        var_ave = np.ma.average(vara[lidx1:lidx2], axis=0)

    return var_ave

