import xarray as xr

def dmy_var(ds,tiempo=None ,accum=None, avg=None, mediana=None):
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


def monthly_clim(ds,stat=None):
    # Falta agregar el periodo de tiempo como entrada
    ds = ds.sel(time=slice('2000-01','2022-12'))
    if stat == 'mean':
        da = ds.resample(time='1M').mean().groupby('time.month').mean('time')
    elif stat == 'median':
        da = ds.resample(time='1M').median().groupby('time.month').mean('time')
    else:
        print('Coloque mean o median como estadístico para la climatología')
    return(da)


def daily_clim(file,var,out):
    
    if var=='PP':
        ds=xr.open_dataset(file,drop_variables=['PP']).rename({'__xarray_dataarray_variable__':'PP'})
    else:    
        ds=xr.open_dataset(file,chunks={})
    
    ds=ds.convert_calendar('365_day').groupby('time.dayofyear').median()
    
    if ds.get(var).ndim == 3:
        mw= xr.DataArray(np.tile(ds.get(var),(3,1,1)),name=var,
             coords={'time':np.tile(ds.coords['dayofyear'].data,3),
                     'lat':ds.coords['lat'].data,
                     'lon':ds.coords['lon'].data},
             dims=('time','lat','lon')).rolling(time=15,center=True).mean().isel(time=np.arange(365,730))
    elif ds.get(var).ndim == 4:
        if var == 'W':
            mw= xr.DataArray(np.tile(ds.get(var),(3,1,1,1)),name=var,
                 coords={'time':np.tile(ds.coords['dayofyear'].data,3),
                         'levs':ds.coords['bottom_top_stag'].data,
                         'lat':ds.coords['lat'].data,
                         'lon':ds.coords['lon'].data},
                 dims=('time','levs','lat','lon')).rolling(time=15,center=True).mean().isel(time=np.arange(365,730))
        else:
            mw= xr.DataArray(np.tile(ds.get(var),(3,1,1,1)),name=var,
                 coords={'time':np.tile(ds.coords['dayofyear'].data,3),
                         'levs':ds.coords['bottom_top'].data,
                         'lat':ds.coords['lat'].data,
                         'lon':ds.coords['lon'].data},
                 dims=('time','levs','lat','lon')).rolling(time=15,center=True).mean().isel(time=np.arange(365,730))
            
    mw.to_netcdf(out)
    print('fin fin')
    return

