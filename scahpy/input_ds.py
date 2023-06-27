import pandas as pd
import numpy as np
import xarray as xr
import wrf
from functools import partial

def _dict_metadata_wrf_vars(da):
    """Append to a dictionary 4 metadata features like stagger, # of dimensions,
       description and the units.
    ES: En un diccionario, usar como llave el nombre de la variables y como items,
    la información de la variables 'staggeada', # de dimensiones, descripción de la variable
    y sus unidades.

    Parameters/Parámetros:
    ----------------------
    da : wrfout dataset already loaded / dataset wrfout ya cargado y leido
    """
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

    Parameters/Parámetros:
    ----------------------
    file0 : Path to any wrfoutfile / Ruta a cualquier archivo wrfout
    printall : True/False , Print variable's info/ Imprime la info de las variables
    """
    da=xr.open_dataset(file0,engine='netcdf4')
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
    """Unstag the stagged coordinates and also assign lat and lon coords.
    ES: Destagea las variables y asigna latitudes y longitudes como coordenadas

    Parameters/Parámetros:
    ----------------------
    file0 : Path to any wrfoutfile / Ruta a cualquier archivo wrfout
    da : wrfout dataset already loaded / dataset wrfout ya cargado y leido
    """
    # Get list of keys that contains the given value
    d0 = xr.open_dataset(file0, engine='netcdf4')
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
    
    for coords in ['XLAT','XLONG','XLAT_U','XLONG_U','XLAT_V','XLONG_V']:
        try:
            da = da.drop_vars(coords)
        except:
            pass
    da = da.rename({'south_north':'lat','west_east':'lon'})
    return da

def _drop_wrf_vars(file0,sel_vars):
    """Save in a list all the variables to be ignored when reading wrfouts files.
    ES: Guarda en una lista todas las variables que no serán leidas.

    Parameters/Parametros:
    ----------------------
    file0 : Path to any wrfoutfile / Ruta a cualquier archivo wrfout
    sel_vars : list of variables to keep / Lista de variables a mantener
    """
    wrf_all_vars=_list_all_WRFvars(file0,False)
    
    list_no_vars = []
    for vari in wrf_all_vars:
        if vari not in sel_vars:
            list_no_vars.append(vari)
    return list_no_vars

def _select_time(x,difHor,sign):
    """Change and assign the time as a coordinate, also it's possible to
    change to local hour.
    ES: Cambia y asigna el tiempo como una coordenada, asímismo es posible
    cambiar a hora local.

    Parameters/Parametros:
    ----------------------
    difHor : String with the hours t / Lista de variables a mantener
    sign: -1 or 1 according to the difference / +1 o -1 dependiendo de
    la diferencia horaria respecto a la UTC
    """
    d = x.rename({'XTIME':'time'}).swap_dims({'Time':'time'})
    time2=pd.to_datetime(d.time.values) + (sign*pd.Timedelta(difHor))
    d=d.assign_coords({'time':time2})
    return d

def ds_wrf(files,list_no_vars,difHor,sign):
    """Read a list of wrfout files for the variables selected.
    ES: Lee una lista de archivos wrfout para las variables seleccionadas.

    Parameters/Parametros:
    ----------------------
    files : List of wrfout files / Lista de archivos wrfout
    list_no_vars : List of variables to be delated / Lista de variables a ignorar
    difHor : String with the hours t / Lista de variables a mantener
    sign: -1 or 1 according to the difference / +1 o -1 dependiendo de
    la diferencia horaria respecto a la UTC
    """
    ds = xr.open_mfdataset(files, combine='nested', concat_dim='time', parallel= True ,engine='netcdf4',
                                drop_variables=list_no_vars, preprocess = partial(_select_time,difHor=difHor,sign=sign))
    ds.attrs = []
    _, index = np.unique(ds['time'], return_index=True)
    ds = ds.isel(time=index)
    ds1 = _new_coords(files[0],ds)
   
    return ds1 
