import xarray as xr
import numpy as np
from wrf import (destagger,interplevel,get_cartopy, latlon_coords, to_np, cartopy_xlim, cartopy_ylim,
                 getvar, ALL_TIMES,cloudfrac)

def dmy_var(ds,tiempo=None ,accum=None, avg=None, mediana=None):
    """Convert hourly (default wrf out) time to any acceptable by resample function.
    ES: Convierte los datos horarios (por defecto wrfout) a otra escala de tiempo 
    aceptada por la función resample (ejm. 'D' diario, 'M' mensual, etc)

    Parameters/Parametros:
    ----------------------
    ds : Dataset loaded / Dataset previamente guardado
    tiempo : Time accepted by resample / tiempo aceptado por la funcion resample
    accum : List of variables who need sum / Si es True, emplea la función suma
    avg : if True use the mean function / Si es True, emplea la función promedio
    mediana : if True use the median function / Si es True, emplea la función mediana
    """
    if accum is not None and avg is None and mediana is None:
        ds_D = ds[accum].resample(time = tiempo).sum()
    elif avg is not None and accum is None and mediana is None:
        ds_D = ds[avg].resample(time = tiempo).mean()
    elif mediana is not None and avg is None and accum is None:
        ds_D = ds[mediana].resample(time = tiempo).median()
    else:
        print('Ingrese una lista de variables en solo uno de los\
               parámetros (accum, avg o mediana) o coloque una\
               escala temporal apropiada')
    return ds_D


def monthly_clim(ds,stat=None,time_slice=None):
    """Convert a Dataset to monthly climatology.
    ES: Convierte el dataset a una climatología mensualizada

    Parameters/Parametros:
    ----------------------
    ds : Dataset loaded / Dataset previamente guardado
    stat : Mean or median  / estadístico para la climatología: Promedio o mediana
    time_slice : use the slice(ini,fin) / Usar slice(ini,fin) con los tiempos iniciales
      y finales
    """
    ds = ds.sel(time=time_slice)
    if stat == 'mean':
        da = ds.resample(time='1M').mean().groupby('time.month').mean('time')
    elif stat == 'median':
        da = ds.resample(time='1M').median().groupby('time.month').mean('time')
    else:
        print('Coloque mean o median como estadístico para la climatología')
    return(da)


def daily_clim(ds,var):
    """  Generate daily climatology using moving window (mw) each 15 days
    ES: Genera climatologías diarias empleando ventanas móviles de 15 dias

    Parameters/Parametros:
    ----------------------
    ds : Dataset loaded / Dataset previamente guardado
    var : str with the variable's name  / string con el nombre de la variable
    """
      
    ds=ds.convert_calendar('365_day').groupby('time.dayofyear').median()
    
    if ds.get(var).ndim == 3:
        mw= xr.DataArray(np.tile(ds.get(var),(3,1,1)),name=var,
             coords={'time':np.tile(ds.coords['dayofyear'].data,3),
                     'lat':ds.coords['lat'].data,
                     'lon':ds.coords['lon'].data},
             dims=('time','lat','lon')).rolling(time=15,center=True).mean().isel(time=np.arange(365,730))
    elif ds.get(var).ndim == 4:
        mw= xr.DataArray(np.tile(ds.get(var),(3,1,1,1)),name=var,
                         coords={'time':np.tile(ds.coords['dayofyear'].data,3),
                                 'levs':ds.coords['bottom_top'].data,
                                 'lat':ds.coords['lat'].data,
                                 'lon':ds.coords['lon'].data},
                                 dims=('time','levs','lat','lon')).rolling(time=15,center=True).mean().isel(time=np.arange(365,730))

    return mw

def vert_levs(ds,vv,lvls):
    """  Interpolate vertical levels to a pressure variable.
    ES: Genera la interpolación vertical de las variables a nivel de presión

    Parameters/Parametros:
    ----------------------
    ds : Dataset loaded / Dataset previamente guardado
    wx : vertical variable dataset  / string con el nombre de la variable
    """

    # Corregir aun el script y mejorar el mensaje.
    plevels=[1000,975,950,925,900,850,800,700,600,500,400,300,200,100,50] # Default
    lvls=plevels
    lats=ds['Presion'].lat.values
    lons=ds['Presion'].lon.values
    timess = ds['Presion'].time.values

    vv_lvl=interplevel(vv,ds.Presion,lvls).assign_coords(lat=lats,lon=lons,time=timess).persist()
    vv_lvl=vv_lvl.to_dataset()

    #vv_lvl.attrs['vert_units'] = ''

    return vv_lvl


