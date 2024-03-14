import pandas as pd
import numpy as np
import xarray as xr
import wrf
from functools import partial
import geopandas as gpd

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

    da['lat'].attrs = {"units": 'degrees_north', 'axis': 'Y','long_name':'Latitude','standard_name':'latitude'}
    da['lon'].attrs = {"units": 'degrees_east', 'axis': 'X','long_name':'Longitude','standard_name':'longitude'}
    
    for var in da:
        da[var].encoding['coordinates'] = 'time lat lon'

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

def ds_wrf_multi(files, list_no_vars, difHor=0, sign=1, save_path=None):
    """
    Read a list of wrfout files for the selected variables and optionally save the resulting netCDF file.

    Parameters:
    -----------
    files : list of str
        List of paths to wrfout files.
    list_no_vars : list
        List of variables to be excluded.
    difHor : str, optional
        String with the hour difference.
    sign : int, optional
        -1 or 1 according to the difference.
    save_path : str, optional
        Path to save the resulting netCDF file.

    Returns:
    --------
    ds1 : xarray.Dataset
        Dataset containing the selected variables.
    """
    # Read the wrfout files and drop specified variables
    ds = xr.open_mfdataset(files, combine='nested', concat_dim='time', parallel=True, engine='netcdf4',
                            drop_variables=list_no_vars, preprocess=partial(_select_time, difHor=difHor, sign=sign))

    # Remove duplicate times
    _, index = np.unique(ds['time'], return_index=True)
    ds = ds.isel(time=index)

    # Update coordinates and encoding
    ds1 = _new_coords(files[0], ds)
    ds1.encoding['unlimited_dims'] = ('time',)

    # Optionally save the resulting netCDF file
    if save_path is not None:
        ds1.to_netcdf(save_path)

    return ds1


def ds_wrf_single(file, list_no_vars, difHor=0, sign=1, save_path=None):
    """
    Read a list of wrfout files for the selected variables and optionally save the resulting netCDF file.

    Parameters:
    -----------
    file : str 
        Path to the wrfout file.
    list_no_vars : list
        List of variables to be excluded.
    difHor : str, optional
        String with the hour difference.
    sign : int, optional
        -1 or 1 according to the difference.
    save_path : str, optional
        Path to save the resulting netCDF file.

    Returns:
    --------
    ds2 : xarray.Dataset
        Dataset containing the selected variables.
    """
    # Read the wrfout file(s) and drop specified variables
    ds = xr.open_dataset(file, engine='netcdf4', drop_variables=list_no_vars)

    # Rename and manipulate time coordinate
    ds1 = ds.rename({'XTIME': 'time'}).swap_dims({'Time': 'time'})
    time2 = pd.to_datetime(ds1.time.values) + (sign * pd.Timedelta(difHor))
    ds1 = ds1.assign_coords({'time': time2})
    ds1.attrs = []

    # Remove duplicate times
    _, index = np.unique(ds1['time'], return_index=True)
    ds1 = ds1.isel(time=index)

    # Update coordinates and encoding
    ds2 = _new_coords(file, ds1)
    ds2.encoding['unlimited_dims'] = ('time',)

    # Optionally save the resulting netCDF file
    if save_path is not None:
        ds2.to_netcdf(save_path)

    return ds2


def extract_station_wrf(out, station, lon_col, lat_col, name_col, output_format='netcdf'):
    """
    Extracts data from a WRF output file using station coordinates provided in a CSV or shapefile.

    Parameters:
    - out (nc): the wrf outfile already laoded.
    - station (str): Path to the CSV or shapefile containing station coordinates.
    - lon_col (str): Name of the column containing longitude values.
    - lat_col (str): Name of the column containing latitude values.
    - name_col (str): Name of the column containing station names.
    - output_format (str, optional): Output format ('netcdf' or 'dataframe'). Defaults to 'netcdf'.

    Returns:
    - Extracted data in the specified format.
    """

    # Read station coordinates from CSV or shapefile
    if station.lower().endswith('.csv'):
        station_data = pd.read_csv(station)
    elif station.lower().endswith('.shp'):
        df = gpd.read_file(station)
        station_data = df.drop('geometry', axis=1)
    else:
        raise ValueError("Unsupported station file format. Supported formats: .csv, .shp")

    # Create xarray dataset with station coordinates
    crd_ix = station_data.set_index(name_col).to_xarray()

    # Select data at nearest grid points to station coordinates
    extracted_data = out.sel(lon=crd_ix[lon_col], lat=crd_ix[lat_col], method='nearest')

    # Convert to DataFrame if the output format is specified as 'dataframe'
    if output_format == 'dataframe':
        extracted_data = extracted_data.to_dataframe().reset_index()

    return extracted_data



