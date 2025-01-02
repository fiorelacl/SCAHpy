import pandas as pd
import numpy as np
import shapefile
import xarray as xr
import datetime
import wrf
from functools import partial

def _dict_metadata_vars(file0,model='wrf'):
    """Append to a dictionary 4 metadata features like stagger, # of dimensions,
       description and the units.
    ES: En un diccionario, usar como llave el nombre de la variables y como items,
    la información de la variables 'staggeada', # de dimensiones, descripción de la variable
    y sus unidades.

    Parameters/Parámetros:
    ----------------------
    da : wrfout/crocoavg dataset already loaded / dataset wrfout o crocoavg ya cargado y leido
    model: 'croco' o 'wrf'
    """
    da=xr.open_dataset(file0,engine='netcdf4')
    a=dict()
    for var in da:
        try:
            if model=='wrf':
                a.setdefault(var,[])
                a[var].append(da[var].stagger)
                a[var].append(len(da[var].dims))
                a[var].append(da[var].description)
                a[var].append(da[var].units)
            elif model=='croco':
                a.setdefault(var,[])
                a[var].append(da[var].dims)
                a[var].append(da[var].long_name)
                a[var].append(da[var].standard_name)
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

def _drop_vars(file0, sel_vars, model='wrf'):
    """Save in a list all the variables to be ignored when reading wrfouts files.
    ES: Guarda en una lista todas las variables que no serán leidas.

    Parameters/Parametros:
    ----------------------
    file0 : Path to any wrfoutfile / Ruta a cualquier archivo wrfout
    sel_vars : list of variables to keep / Lista de variables a mantener
    """

    ds_all_vars = list(_dict_metadata_vars(file0,model).keys())
    
    list_no_vars = []
    for vari in ds_all_vars:
        if vari not in sel_vars:
            list_no_vars.append(vari)
    return list_no_vars

def _new_wrf_coords(file0,da):
    """Unstag the stagged coordinates and also assign lat and lon coords.
    ES: Destagea las variables y asigna latitudes y longitudes como coordenadas

    Parameters/Parámetros:
    ----------------------
    file0 : Path to any wrfoutfile / Ruta a cualquier archivo wrfout
    da : wrfout dataset already loaded / dataset wrfout ya cargado y leido
    """
    # Get list of keys that contains the given value
    d0 = xr.open_dataset(file0, engine='netcdf4')
    b = _dict_metadata_vars(file0,'wrf')

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

def _new_croco_coords(da,file0):
    """Unstag the stagged coordinates and also assign lat and lon coords.
    ES: Destagea las variables y asigna latitudes y longitudes como coordenadas

    Parameters/Parámetros:
    ----------------------
    da : croco output dataset already loaded / dataset output ya cargado y leido
    """

    ds_meta = _dict_metadata_vars(file0,'croco')
    lats = da.lat_rho.isel(xi_rho=0).values
    lons = da.lon_rho.isel(eta_rho=0).values
    levs = da.s_rho.values

    list_X = [key for key, list_values in ds_meta.items() if 'xi_u' in list_values[0]]
    list_Y = [key for key, list_values in ds_meta.items() if 'eta_v' in list_values[0]]
    list_Z = [key for key, list_values in ds_meta.items() if 's_w' in list_values[0]]
    list_otros = [key for key, list_values in ds_meta.items() if 'xi_u' not in list_values[0] and
                      'eta_v' not in list_values[0] and
                      's_w' not in list_values[0]]

    da_nostagxy = da[list_otros+list_Z]
    da_stagx = da[list_X]
    da_stagy = da[list_Y]

    for var in da_nostagxy:
        if var in list_Z:
            try:
                da_nostagxy[var] = wrf.destagger(da_nostagxy[var],stagger_dim=1,meta=True)
                da_nostagxy[var] = da_nostagxy[var].rename({'dim_1':'s_rho'})
            except:
                da_nostagxy[var] = wrf.destagger(da_nostagxy[var],stagger_dim=0,meta=True)
                da_nostagxy[var] = da_nostagxy[var].rename({'dim_0':'s_rho'})
                pass

    da_nostagxy["xi_rho"] = ("xi_rho", lons)
    da_nostagxy["eta_rho"] = ("eta_rho", lats)

    da_nostagxy = da_nostagxy.drop_vars(['lat_rho','lon_rho'])

    for var in da_stagx:
            da_stagx[var] = wrf.destagger(da_stagx[var],stagger_dim=-1,meta=True)

            new_dim = [dim for dim in da_stagx[var].dims if 'dim_' in dim]        
            if new_dim:
                da_stagx[var] = da_stagx[var].rename({new_dim[0]:'xi_rho'})

    da_stagx["xi_rho"] = ("xi_rho", lons[1:-1])
    da_stagx["eta_rho"] = ("eta_rho", lats)
    da_stagx = da_stagx.drop_vars(['lat_u','lon_u','xi_u'])

    for var in da_stagy:
            da_stagy[var] = wrf.destagger(da_stagy[var],stagger_dim=-2,meta=True)

            new_dim = [dim for dim in da_stagy[var].dims if 'dim_' in dim]        
            if new_dim:
                da_stagy[var] = da_stagy[var].rename({new_dim[0]:'eta_rho'}) 

    da_stagy["xi_rho"] = ("xi_rho", lons)
    da_stagy["eta_rho"] = ("eta_rho", lats[1:-1])
    da_stagy = da_stagy.drop_vars(['lat_v','lon_v','eta_v'])

    ds_croco = xr.merge([da_nostagxy,da_stagx,da_stagy],join='outer')

    ds_croco = ds_croco.rename({'eta_rho':'lat','xi_rho':'lon','s_rho':'levels'})
    ds_croco['lat'].attrs = {"units": 'degrees_north', 'axis': 'Y','long_name':'Latitude','standard_name':'latitude'}
    ds_croco['lon'].attrs = {"units": 'degrees_east', 'axis': 'X','long_name':'Longitude','standard_name':'longitude'}

    for var in ds_croco:
        ds_croco[var].encoding['coordinates'] = 'time lat lon'
        
    return ds_croco

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

def read_wrf_multi(files, list_no_vars, difHor=0, sign=1, save_path=None):
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
    ds1 = _new_wrf_coords(files[0], ds)
    ds1.encoding['unlimited_dims'] = ('time',)

    # Optionally save the resulting netCDF file
    if save_path is not None:
        ds1.to_netcdf(save_path)

    return ds1

def read_wrf_single(file, list_no_vars, difHor=0, sign=1, save_path=None):
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
    ds2 = _new_wrf_coords(file, ds1)
    ds2.encoding['unlimited_dims'] = ('time',)

    # Optionally save the resulting netCDF file
    if save_path is not None:
        ds2.to_netcdf(save_path)

    return ds2

def read_croco(files, list_no_vars, save_path=None):
    """
    Read a list of wrfout files for the selected variables and optionally save the resulting netCDF file.

    Parameters:
    -----------
    files : list of str
        List of paths to croco files.
    list_no_vars : list
        List of variables to be excluded.
    save_path : str, optional
        Path to save the resulting netCDF file.

    Returns:
    --------
    ds1 : xarray.Dataset
        Dataset containing the selected variables.
    """
    # Read the wrfout files and drop specified variables
    ds = xr.open_mfdataset(files, combine='nested', concat_dim='time', parallel=True, engine='netcdf4',
                            drop_variables=list_no_vars)

    epoch = datetime.datetime(1900, 1, 1)
    time_datetimes = [epoch + datetime.timedelta(seconds=int(sec)) for sec in ds.time.values]

    # Convierte la lista de datetime a una serie de pandas (Pandas DatetimeIndex)
    time_index = pd.to_datetime(time_datetimes)

    ds['time']=time_index
    
    # Remove duplicate times
    _, index = np.unique(ds['time'], return_index=True)
    ds = ds.isel(time=index)

    # Update coordinates and encoding
    ds1 = _new_croco_coords(ds, files[0])
    ds1.encoding['unlimited_dims'] = ('time',)

    # Optionally save the resulting netCDF file
    if save_path is not None:
        ds1.to_netcdf(save_path)

    return ds1

def extract_station_wrf(out, station, lon_col, lat_col, name_col, output_format='netcdf', save_path=None):
    """
    Extracts data from a WRF output file using station coordinates provided in a CSV or shapefile.

    Parameters:
    - out (nc): the wrf outfile already loaded.
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
        # Use pyshp to read shapefile
        sf = shapefile.Reader(station)
        fields = [field[0] for field in sf.fields[1:]]  # Skip 'DeletionFlag'
        records = sf.records()
        shapes = sf.shapes()
        
        # Combine attributes and geometry into a DataFrame
        station_data = pd.DataFrame(records, columns=fields)
        station_data['lon'] = [shape.points[0][0] for shape in shapes]
        station_data['lat'] = [shape.points[0][1] for shape in shapes]
    else:
        raise ValueError("Unsupported station file format. Supported formats: .csv, .shp")

    # Create xarray dataset with station coordinates
    crd_ix = station_data.set_index(name_col).to_xarray()

    # Select data at nearest grid points to station coordinates
    extracted_data = out.sel(lon=crd_ix[lon_col], lat=crd_ix[lat_col], method='nearest')

    # Convert to DataFrame if the output format is specified as 'dataframe'
    if output_format == 'dataframe':
        extracted_data = extracted_data.to_dataframe().reset_index()

    if save_path is not None and output_format == 'dataframe':
       extracted_data.to_csv(save_path)
    elif save_path is not None and output_format == 'netcdf':
       extracted_data.to_netcdf(save_path)

    return extracted_data



