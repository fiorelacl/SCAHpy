import xarray as xr
import shapefile
import numpy as np
import pandas as pd

def destagger_array(da: xr.DataArray, axis: str) -> xr.DataArray:
    """
    Removes staggering along a given dimension by averaging adjacent values.

    Parameters
    ----------
    da : xr.DataArray
        The staggered variable to be destaggered.

    axis : str
        Name of the staggered dimension to collapse.
        Examples:
            - WRF: 'west_east_stag', 'south_north_stag', 'bottom_top_stag', 'soil_layers_stag'
            - CROCO: 'xi_u', 'eta_v', 's_w'

    Returns
    -------
    xr.DataArray
        The destaggered array, with the specified dimension size reduced by 1.
    """
    if axis not in da.dims:
        raise ValueError(f"Axis '{axis}' not found in DataArray dimensions: {da.dims}")

    axis_index = da.get_axis_num(axis)

    slices_a = [slice(None)] * da.ndim
    slices_b = [slice(None)] * da.ndim
    slices_a[axis_index] = slice(0, -1)
    slices_b[axis_index] = slice(1, None)

    da_unstaggered = 0.5 * (da[tuple(slices_a)] + da[tuple(slices_b)])
    da_unstaggered.name = da.name
    da_unstaggered.attrs = da.attrs.copy()  # safer copy of attributes

    return da_unstaggered

def wrfinterp_vert_levels(ds,varis,lvls=None):
    """  Interpolate vertical levels to a pressure variable.
    ES: Genera la interpolación vertical de las variables a nivel de presión, considera
    que la variable temporal se llama 'time', de no ser así, renombrar a 'time'

    Parameters/Parametros:
    ----------------------
    ds : Dataset loaded / Dataset previamente guardado
    varis : list of variables  / Lista de variables a ser interpoladas
    """
    if lvls is None:
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
    ds_lvl = xr.merge(datasets)
    ds_lvl.encoding['unlimited_dims']=('time',)
    ds_lvl['lat'].attrs = {"units": 'degrees_north', 'axis': 'Y','long_name':'Latitude','standard_name':'latitude'}
    ds_lvl['lon'].attrs = {"units": 'degrees_east', 'axis': 'X','long_name':'Longitude','standard_name':'longitude'}

    return ds_lvl

def crocointerp_sigma_z(ds,varis,lvls=None):
    """  Interpolate sigma levels to z.
    ES: Genera la interpolación vertical de las variables a nivel de presión, considera
    que la variable temporal se llama 'time', de no ser así, renombrar a 'time'

    Parameters/Parametros:
    ----------------------
    ds : Dataset loaded / Dataset previamente guardado
    varis : list of variables  / Lista de variables a ser interpoladas
    """
    if lvls is None:
        plevels=[-1000,-950,-900,-850,-800,-750,-700,-650,-600,-550,-500,
                 -475,-450,-425,-400,-375,-350,-325,-300,-290,-280,-275,
                 -270,-260,-250,-240,-230,-225,-220,-210,-200,-190,-180,
                 -175,-170,-160,-150,-140,-130,-125,-120,-110,-100,-90,
                 -80,-75,-70,-60,-50,-40,-30,-20,-10,-5,0] # Default
        lvls=plevels

    if 'zlevs' not in ds:        
        ds['zlevs']= ds.zeta + ((ds.zeta+ds.h)*ds.levels)
        zlevs = ds["zlevs"]
        zlevs_reordered = zlevs.transpose("time", "levels", "lat", "lon")
        ds["zlevs"] = zlevs_reordered

    lats=ds['zlevs'].lat.values
    lons=ds['zlevs'].lon.values
    timess = ds['zlevs'].time.values

    datasets = []
    for var in varis:
        dlvl=interplevel(ds[var],ds.zlevs,lvls).assign_coords(lat=lats,lon=lons,time=timess).rename({'level':'zlevel'}).persist()
        dlvl=dlvl.to_dataset().rename({f'{var}_interp':f'{var}'})
        dlvl[var].attrs['vert_units'] = 'm'
        dlvl[var].encoding['coordinates'] = 'time lat lon'
        datasets.append(dlvl)
    ds_lvl = xr.merge(datasets)
    ds_lvl.encoding['unlimited_dims']=('time',)
    ds_lvl['lat'].attrs = {"units": 'degrees_north', 'axis': 'Y','long_name':'Latitude','standard_name':'latitude'}
    ds_lvl['lon'].attrs = {"units": 'degrees_east', 'axis': 'X','long_name':'Longitude','standard_name':'longitude'}

    return ds_lvl

def extract_point_data(out, station, lon_col, lat_col, name_col, output_format='netcdf', save_path=None):
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
