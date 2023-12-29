import xarray as xr
from wrf import (interplevel)

def vert_levs(ds,varis,lvls):
    """  Interpolate vertical levels to a pressure variable.
    ES: Genera la interpolación vertical de las variables a nivel de presión

    Parameters/Parametros:
    ----------------------
    ds : Dataset loaded / Dataset previamente guardado
    wx : vertical variable dataset  / string con el nombre de la variable
    """

    plevels=[1000,975,950,925,900,850,800,700,600,500,400,300,200] # Default
    lvls=plevels

    if 'Presion' not in ds:
        ds['Presion']= (ds['P']+ds['PB'])/100

    lats=ds['Presion'].lat.values
    lons=ds['Presion'].lon.values
    timess = ds['Presion'].time.values

    datasets = []
    for var in varis:
        dlvl=interplevel(ds[var],ds.Presion,lvls).assign_coords(lat=lats,lon=lons,time=timess).persist()
        dlvl=dlvl.to_dataset().rename({f'{var}_interp':f'{var}'})
        dlvl[var].attrs['vert_units'] = ''
        dlvl[var].encoding['coordinates'] = 'time lat lon'
        datasets.append(dlvl)
    ds_lvl = xr.concat(datasets,dim='time')
    ds_lvl.encoding['unlimited_dims']=('time',)
    ds_lvl['lat'].attrs = {"units": 'degrees_north', 'axis': 'Y','long_name':'Latitude','standard_name':'latitude'}
    ds_lvl['lon'].attrs = {"units": 'degrees_east', 'axis': 'X','long_name':'Longitude','standard_name':'longitude'}

    return ds_lvl

