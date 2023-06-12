import pandas as pd
import xarray as xr
import wrf

def _dict_metadata_wrf_vars(da):
    a=dict()
    for var in da:
        try:
            a.setdefault(var,[])
            a[var].append(da[var].stagger)
            a[var].append(len(da[var].dims))
            a[var].append(da[var].description)
            a[var].append(da[var].units)
        except:
            pass
    return a

def _list_all_WRFvars(file0,printall):
    """Read one wrfout file and list all the variables.
    ES: Lee un archivo wrfout y lista todas las variables.
    """
    da=xr.open_dataset(file0)
    for var in da:
        try:
            if printall:
                # print(var)
                print(f'{var}, Stagger: {da[var].stagger}, Description: {da[var].description}, Units: {da[var].units}')
        except:
            pass
    wrf_name_vars = list(_dict_metadata_wrf_vars(da).keys())
    return wrf_name_vars


def _new_coords(file0,da):
    # Get list of keys that contains the given value
    d0 = xr.open_dataset(file0)
    b = _dict_metadata_wrf_vars(da)

    list_X_keys = [key for key, list_of_values in b.items() if 'X' in list_of_values]
    list_Y_keys = [key for key, list_of_values in b.items() if 'Y' in list_of_values]
    list_Z_keys = [key for key, list_of_values in b.items() if 'Z' in list_of_values]

    #destagger dim0=Time, dim1=bottom_top, dim2=south_north, dim3=west_east
    for var in da:
        if var in list_X_keys:
            da[var] = wrf.destagger(da[var],stagger_dim=-1,meta=True)
        elif var in list_Y_keys:
            da[var] = wrf.destagger(da[var],stagger_dim=-2,meta=True)
        elif var in list_Z_keys:
            da[var] = wrf.destagger(da[var],stagger_dim=1,meta=True)

    da = da.assign_coords(south_north=('south_north',d0.XLAT[0,:,0].values))
    da = da.assign_coords(west_east=('west_east',d0.XLONG[0,0,:].values))  
    return da

def _drop_wrf_vars(file0,sel_vars):
    """Save in a list all the variables to ignore when reading wrfouts files.
    ES: Guarda en una lista todas las variables que no serán leidas.

    Parameters/Parametros:
    ----------------------
    file0 : Path to any wrfoutfile / Ruta a cualquier archivo wrfout
    sel_vars : list of variables to keep / Lista de variables a mantener
    """
    wrf_all_vars=_list_all_WRFvars(file0)
    
    list_no_vars = []
    for vari in wrf_all_vars:
        if vari not in sel_vars:
            list_no_vars.append(vari)
    return list_no_vars

def _select_time(x,yi,yf,mi,mf,difHor):
    d = x.rename({'XTIME':'time'}).swap_dims({'Time':'time'})
    time2=pd.to_datetime(d.time.values)-pd.Timedelta(difHor)
    d=d.assign_coords({'time':time2})
    return d.sel(time=slice(f'{yi}-{mi}',f'{yf}-{mf}'))

def ds_wrf(files,list_no_vars,var,yn):
    d0 = xr.open_mfdataset(files, combine='nested', concat_dim='time', parallel= True ,engine='netcdf4',
                                drop_variables=list_no_vars, preprocess = partial(_select_time, yi,yf,mi,mf,difHor))
    d0.attrs = []
    ntime = d0.time[0:-1]
    # _, index = np.unique(d0['XTIME'], return_index=True)
    # d = d0.isel(Time=index)
    if var == 'PP':
        d0 = d0.RAINC + d0.RAINSH + d0.RAINNC
        d0['PP'] = d0
        d0 = d0.PP.diff('time')
        d0['time'] = ntime
        # d0 = d0.resample(time='1D').sum()
        d0 = d0.load()
        dg = _new_coords(files[0],d0) # Decidir si va a guardar los archivos o si se usará el Dataset sin guardar.
        time2=pd.to_datetime(dg.time.values)-pd.Timedelta('5 hours')
        dg=dg.assign_coords({'time':time2})
        dd=dg.resample(time='1D').sum()
        print('La variable es Precipitación')
    # elif var == 'T2':
    #     d0=0.5*(d0.resample(time='1D').min() + d0.resample(time='1D').max()) #d.T2[3::8,:,:] + d.T2[6::8,:,:]
    #     print('La variable es Temperatura del aire a 2m')
    else:
        print('Carga :D')
        # d0 = d0.resample(time='1D').mean()
        d0 = d0.load()
        print('Variable general (no PP) Mensual')
        dg = _new_coords(files[0],d0) # Decidir si va a guardar los archivos o si se usará el Dataset sin guardar.
        time2=pd.to_datetime(dg.time.values)-pd.Timedelta('5 hours')
        dg=dg.assign_coords({'time':time2})
        dd=dg.resample(time='1D').mean()
    print('guardando')    
    
    return dd 