import xarray as xr
import numpy as np
import matplotlib.pyplot as plt 
import cmocean
from cmcrameri import cm
import cartopy.feature as cfe
from cartopy.io.shapereader import Reader
import matplotlib
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from matplotlib.cm import get_cmap
import matplotlib.colors as colors


def plot_PP_SST_UV10(pp,tsm,uv10):

    lons=pp.lon.values
    lats=pp.lat.values
    timess = pp.time.values

    #levs=[1,2,3,5,7,11,15,20,25,30,35,40,45,50,55,60] # 3HR
    levs=[0,25,50,100,200,400,600,800,1000,1200,1400,1600] # mm/dia
    levs2=[26,27,28]
    cmaps=cmocean.tools.lighten(cmocean.cm.rain, 0.85)

    sa = cfe.ShapelyFeature(Reader('/data/users/fcastillon/shapes/SA_paises.shp').geometries(), ccrs.PlateCarree(), edgecolor='k', facecolor='none') #d3d3d3
    z12 = cfe.ShapelyFeature(Reader('/data/users/fcastillon/shapes/Z12.shp').geometries(), ccrs.PlateCarree(), edgecolor='r', facecolor='none')
    norm = matplotlib.colors.BoundaryNorm(levs, cmaps.N)

    tsm['SSTSK']=tsm['SSTSK']-273.15          
    tt=str(timess[t])[0:7]

    fig,axs = plt.subplots(figsize=(12,10),ncols=1,nrows=1,sharex=True,sharey=True,subplot_kw=dict(projection=ccrs.PlateCarree()))

    pcm=axs.contourf(lons,lats,pp.PP.isel(time=t),levels=levs,
                        cmap=cmaps,norm=norm,extend='max',transform=ccrs.PlateCarree())
    fig.colorbar(pcm,ax=axs,label='mm/mes', orientation='vertical', shrink=.7,pad=0.07,aspect=20, format='%3.0f')
    c=axs.contour(lons,lats,tsm.get('SSTSK').isel(time=t),
                    levels=levs2,colors=['#F29727','#C70039','#511F73'],
                    linewidths=[1.5,1.6,1.8],linestyles='solid',
                    alpha=0.45,transform=ccrs.PlateCarree(),zorder=7)
    axs.clabel(c, levels=levs2,inline=False,colors='#000000', fontsize=12,zorder=9)
    Q=axs.quiver(lons[::5],lats[::5],
                    uv10.U10.isel(time=t)[::5,::5],uv10.V10.isel(time=t)[::5,::5],
                    scale=150,headwidth=5,headlength=7)
    axs.quiverkey(Q,0.87,1.02,10,f'10 m/s',labelpos='E',coordinates='axes',labelsep=0.05)


    axs.add_feature(sa,linewidth=0.6)
    #ax.add_feature(z12,linewidth=1.2)
    lon_formatter = LongitudeFormatter()
    lat_formatter = LatitudeFormatter()
    axs.yaxis.set_major_formatter(lat_formatter)
    axs.xaxis.set_major_formatter(lon_formatter)
    axs.set_xticks(np.arange(-90, -60, 5), crs=ccrs.PlateCarree())
    axs.set_yticks(np.arange(-20, 5, 5), crs=ccrs.PlateCarree())
    axs.set_extent([-94, -68, -22, 4.2])
    #ax.gridlines(xlocs=[-65,-70,-75,-80,-85,-90],ylocs=[-20,-15,-10,-5,0],linewidth=0.5, color='gray', linestyle='--')  


    plt.title(f'{tt}')#x,y f'{i:05d}'
    plt.savefig(f'/data/users/fcastillon/figuras/{caso}_ANOM_PPm_PRONOS_{tt}.png',
                    bbox_inches='tight',facecolor='white', transparent=False)
    plt.close()