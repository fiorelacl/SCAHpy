import xarray as xr
import numpy as np

def dmy_var(ds, tiempo=None, accum=None, avg=None, mediana=None):
    """Convert hourly (default wrf out) time to any acceptable by resample function.
    ES: Convierte los datos horarios (por defecto wrfout) a otra escala de tiempo 
    aceptada por la función resample (ejm. 'D' diario, 'M' mensual, etc)

    Parameters/Parametros:
    ----------------------------------------------------------------------------------
    ds : Dataset loaded / Dataset previamente guardado
    tiempo : Time accepted by resample / tiempo aceptado por la funcion resample
    accum : List of variables who need sum / Si es True, emplea la función suma
    avg : if True use the mean function / Si es True, emplea la función promedio
    mediana : if True use the median function / Si es True, emplea la función mediana
    """

    datasets = []

    if accum is not None:
        ds_ac = ds[accum].resample(time=tiempo).sum()
        datasets.append(ds_ac)

    if avg is not None:
        ds_avg = ds[avg].resample(time=tiempo).mean()
        datasets.append(ds_avg)

    if mediana is not None:
        ds_med = ds[mediana].resample(time=tiempo).median()
        datasets.append(ds_med)

    if not datasets:  # If no datasets were created
        print('Ingrese al menos una variable para operar.')
        return None

    try:
        ds_all = xr.merge(datasets)
    except ValueError:
        print('Coloque una escala temporal apropiada')
        return None

    return ds_all


def monthly_avg(ds,stat=None,time_slice=None):
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
        print('Coloque mean o median como estadístico para el cálculo')
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

