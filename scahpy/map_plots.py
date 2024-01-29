import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfe
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from cartopy.io.shapereader import Reader
import cmocean
import matplotlib.colors

def m_pp_uv10_sst(pp, sfc, levs, levs2, sa_shapefile, output_path=None, month_list=None,
                           save_maps=True, quiverkey_speed=5,extent=None):
    """
    Plots precipitation maps for specified months.

    Parameters:
    - pp (xarray.Dataset): Precipitation data.
    - sfc (xarray.Dataset): Surface data with SST and UV10 data.
    - levs (list): Contour levels for precipitation.
    - levs2 (list): Contour levels for SSTSK.
    - sa_shapefile (str): Path to the shapefile for South America countries (could be any other).
    - output_path (str, optional): Path to save the maps. If None, maps will be displayed but not saved. Defaults to None.
    - month_list (list, optional): List of months to plot. Defaults to None (all months).
    - save_maps (bool, optional): If True, saves the maps. If False, only displays them. Defaults to True.
    - quiverkey_speed (int, optional): Speed parameter for quiverkey. Defaults to 5.
    - extent: [x1,x2,y1,y2] spatial extension
    """
    cmaps = cmocean.tools.lighten(cmocean.cm.rain, 0.85)
    norm = matplotlib.colors.BoundaryNorm(levs, cmaps.N)

    lons = pp.lon.values
    lats = pp.lat.values

    sa = cfe.ShapelyFeature(Reader(sa_shapefile).geometries(), ccrs.PlateCarree(), edgecolor='k', facecolor='none')

    if month_list is None:
        month_list = range(1, 13)

    for month in month_list:
        fig, axs = plt.subplots(figsize=(13, 12), ncols=1, nrows=1, sharex=True, sharey=True,
                                subplot_kw=dict(projection=ccrs.PlateCarree()))

        pcm = axs.contourf(lons, lats, pp.sel(month=month), levels=levs,
                            cmap=cmaps, norm=norm, extend='both', transform=ccrs.PlateCarree())
        fig.colorbar(pcm, ax=axs, label='mm/month', orientation='vertical', shrink=.7, pad=0.07, aspect=20, format='%3.0f')
        c = axs.contour(lons, lats, sfc.get('SSTSK').sel(month=month),
                        levels=levs2, colors=['#F29727', '#C70039', '#511F73'],
                        linewidths=[1.5, 1.6, 1.8], linestyles='solid',
                        alpha=0.45, transform=ccrs.PlateCarree(), zorder=7)
        axs.clabel(c, levels=levs2, inline=False, colors='#000000', fontsize=12, zorder=9)
        Q = axs.quiver(lons[::7], lats[::7],
                        sfc.U10.sel(month=month)[::7, ::7], sfc.V10.sel(month=month)[::7, ::7],
                        headwidth=5, headlength=7)
        axs.quiverkey(Q, 0.87, 1.02, quiverkey_speed, f'{quiverkey_speed} m/s', labelpos='E', coordinates='axes', labelsep=0.05)

        axs.add_feature(sa, linewidth=0.7, zorder=7)
        lon_formatter = LongitudeFormatter()
        lat_formatter = LatitudeFormatter()
        axs.yaxis.set_major_formatter(lat_formatter)
        axs.xaxis.set_major_formatter(lon_formatter)
        axs.set_extent(extent)

        plt.title(f'Map of Precipitation Month: {month:02d}')

        if save_maps:
            if output_path is None:
                raise ValueError("Output path cannot be None when saving maps.")
            plt.savefig(f'{output_path}/m_TSM_UV_PP_{month}.png',
                        bbox_inches='tight', dpi=300, facecolor='white', transparent=False)
        else:
            plt.show()

        plt.close()

