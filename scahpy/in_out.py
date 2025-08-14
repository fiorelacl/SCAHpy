import pandas as pd
import numpy as np
import xarray as xr
import datetime
from .spatial_scales import destagger_array
from functools import partial

def get_metadata_vars(dataset: str | xr.Dataset, model: str = 'WRF', print_all: bool = False) -> dict[str,list]:
    """
    Extracts metadata for each variable in a NetCDF dataset produced by the WRF or CROCO models.

    Parameters
    ----------
    dataset : str | xr.Dataset
        Path to a NetCDF file or an already opened xarray Dataset.

    model : {'WRF', 'CROCO'}, default='WRF'
        The model that produced the dataset. Accepts 'WRF' or 'CROCO'.

    print_all : bool, default=False
        If True, prints the metadata for each variable.

    Returns
    -------
    dict[str, list]
        A dictionary where each key is a variable name and the value is a list containing:
        
        For WRF:
            - dimensions (tuple of str)
            - units (str or None)
            - stagger (str or None)
            - description (str or None)
        
        For CROCO:
            - dimensions (tuple of str)
            - units (str or None)
            - long_name (str or None)
            - standard_name (str or None)
    
    """
    
    model = model.upper()

    if model not in {'WRF', 'CROCO'}:
        raise ValueError(f"Unrecognized model '{model}'. Choose 'WRF' or 'CROCO'.")

    if isinstance(dataset, str):
        da = xr.open_dataset(dataset, engine='netcdf4')
        close_after = True
    else:
        da = dataset
        close_after = False

    metadata = {}

    try:
        for var in da:
            metadata.setdefault(var, [])
            dims = da[var].dims
            units = da[var].attrs.get('units', None)
            metadata[var].append(dims)
            metadata[var].append(units)

            if model == 'WRF':
                stagger = da[var].attrs.get('stagger', None)
                description = da[var].attrs.get('description', None)
                metadata[var].append(stagger)
                metadata[var].append(description)
                if print_all:
                    print(f"{var}, Stagger: {stagger}, Dims: {dims}, Description: {description}, Units: {units}")

            elif model == 'CROCO':
                long_name = da[var].attrs.get('long_name', None)
                standard_name = da[var].attrs.get('standard_name', None)
                metadata[var].append(long_name)
                metadata[var].append(standard_name)
                if print_all:
                    print(f"{var}, Dims: {dims}, Long name: {long_name}, Standard name: {standard_name}, Units: {units}")
    finally:
        if close_after:
            da.close()

    return metadata

def drop_vars(file0: str | xr.Dataset, sel_vars: list[str], model: str ='WRF') -> list[str]:
    """
    Identifies variables in a NetCDF dataset that are not included 
    in the user-specified selection.

    Parameters
    ----------
    file0 : str | xr.Dataset
        Path to the NetCDF output file or an xarray.Dataset.

    sel_vars : list[str]
        List of variable names the user wants to keep.

    model : {'WRF', 'CROCO'}, default='WRF'
        Model that generated the dataset.

    Returns
    -------
    list[str]
        List of variable names that are present in the dataset but not included in `sel_vars`
    """

    all_vars = set(get_metadata_vars(file0, model).keys())
    sel_vars_set = set(sel_vars)

    return list(all_vars - sel_vars_set)

def _new_wrf_coords( ds_wrf: xr.Dataset, ds_meta: dict[str, list], lats: list | xr.DataArray, lons: list | xr.DataArray,
    destag: bool = True, lats_v: list | xr.DataArray = None, lons_u: list | xr.DataArray = None) -> xr.Dataset:
    
    """
    Applies coordinate transformation and destaggering to a WRF output dataset.

    Parameters
    ----------
    ds_wrf : xr.Dataset
        Dataset containing WRF model output.

    ds_meta : dict[str, list]
        Dictionary of metadata extracted from the dataset using `get_metadata_vars`.

    lats : list | xr.DataArray
        Latitude array for the unstaggered Y-coordinate ('south_north').

    lons : list | xr.DataArray
        Longitude array for the unstaggered X-coordinate ('west_east').

    destag : bool, default=True
        Whether to apply destaggering to variables with staggered dimensions.

    lats_v : list | xr.DataArray, optional
        Latitude array for the V grid (only used if `destag=False`).

    lons_u : list | xr.DataArray, optional
        Longitude array for the U grid (only used if `destag=False`).

    Returns
    -------
    xr.Dataset
        Dataset with standardized and renamed coordinates, with optional destaggering.
    """
 
    list_X_keys = [key for key, list_values in ds_meta.items() if 'west_east_stag' in list_values[0]]
    list_Y_keys = [key for key, list_values in ds_meta.items() if 'south_north_stag' in list_values[0]]
    list_Z_keys = [key for key, list_values in ds_meta.items() if 'bottom_top_stag' in list_values[0]]
    list_S_keys = [key for key, list_values in ds_meta.items() if 'soil_layers_stag' in list_values[0]]

    if destag:
        for var in ds_wrf:
            if var in list_X_keys:
                ds_wrf[var] = destagger_array(ds_wrf[var],axis='west_east_stag').rename({'west_east_stag':'west_east'})
            elif var in list_Y_keys:
                ds_wrf[var] = destagger_array(ds_wrf[var],axis='south_north_stag').rename({'south_north_stag':'south_north'})
            elif var in list_Z_keys:
                ds_wrf[var] = destagger_array(ds_wrf[var],axis='bottom_top_stag').rename({'bottom_top_stag':'bottom_top'})
            elif var in list_S_keys:
                ds_wrf[var] = destagger_array(ds_wrf[var],axis='soil_layers_stag').rename({'soil_layers_stag':'soil_layers'})
    else:
        for var in ds_wrf:
            if var in list_X_keys:
                ds_wrf[var] = ds_wrf[var].assign_coords(west_east_stag=('west_east_stag',lons_u)).rename({'west_east_stag':'lons_u'})
            elif var in list_Y_keys:
                ds_wrf[var] = ds_wrf[var].assign_coords(south_north_stag=('south_north_stag',lats_v)).rename({'south_north_stag':'lats_v'})

    ds_wrf = ds_wrf.assign_coords(south_north=('south_north',lats))
    ds_wrf = ds_wrf.assign_coords(west_east=('west_east',lons))

    drop_coords = ['XLAT', 'XLONG', 'XLAT_U', 'XLONG_U', 'XLAT_V', 'XLONG_V']
    ds_wrf = ds_wrf.drop_vars([c for c in drop_coords if c in ds_wrf.variables], errors='ignore')

    ds_wrf = ds_wrf.rename({'south_north':'lat','west_east':'lon'})

    ds_wrf['lat'].attrs = {"units": 'degrees_north', 'axis': 'Y','long_name':'Latitude','standard_name':'latitude'}
    ds_wrf['lon'].attrs = {"units": 'degrees_east', 'axis': 'X','long_name':'Longitude','standard_name':'longitude'}

    for var in ds_wrf.data_vars:
        coords = ds_wrf[var].coords
        if all(c in coords for c in ['lat', 'lon', 'time']):
            ds_wrf[var].encoding['coordinates'] = 'time lat lon'
    return ds_wrf

def _new_croco_coords(da: xr.Dataset, ds_meta: dict[str, list], lats: list | xr.DataArray, lons: list | xr.DataArray,
    destag: bool = True, lats_v: list | xr.DataArray = None, lons_u: list | xr.DataArray = None) -> xr.Dataset:
    """
    Applies coordinate standardization and destaggering to CROCO output data.

    Parameters
    ----------
    da : xr.Dataset
        CROCO output dataset.

    ds_meta : dict[str, list]
        Metadata dictionary from `get_metadata_vars`.

    lats : list | xr.DataArray
        Latitude array along eta_rho.

    lons : list | xr.DataArray
        Longitude array along xi_rho.

    destag : bool, default=True
        Whether to apply destaggering to staggered dimensions.

    lats_v : list | xr.DataArray, optional
        Latitude for eta_v (only used if `destag=False`).

    lons_u : list | xr.DataArray, optional
        Longitude for xi_u (only used if `destag=False`).

    Returns
    -------
    xr.Dataset
        Standardized and optionally destaggered CROCO dataset with renamed coordinates.
    """
    vars_select = list(da.variables)

    list_X = [key for key, list_values in ds_meta.items() if 'xi_u' in list_values[0]]
    list_Y = [key for key, list_values in ds_meta.items() if 'eta_v' in list_values[0]]
    list_Z = [key for key, list_values in ds_meta.items() if 's_w' in list_values[0]]
    list_otros = [key for key, list_values in ds_meta.items() if 'xi_u' not in list_values[0] and
                      'eta_v' not in list_values[0] and
                      's_w' not in list_values[0]]
    list_ot = list_otros + list_Z

    da_nostagxy = da[[value for value in list_ot if value in vars_select]]
    da_stagx = da[[value for value in list_X if value in vars_select]]
    da_stagy = da[[value for value in list_Y if value in vars_select]]
    
    if destag:
        for var in da_nostagxy:
            if var in list_Z:
                da_nostagxy[var] = destagger_array(da_nostagxy[var],axis='s_w')

        for var in da_stagx:
                da_stagx[var] = destagger_array(da_stagx[var],axis = 'xi_u').rename({'xi_u':'xi_rho'})
                da_stagx[var] = da_stagx[var].assign_coords(xi_rho = ('xi_rho',lons[1:-1]),
                                                            eta_rho = ('eta_rho', lats))
        da_stagx = da_stagx.drop_vars(['lat_u','lon_u'])

        for var in da_stagy:
                da_stagy[var] = destagger_array(da_stagy[var],axis='eta_v').rename({'eta_v':'eta_rho'})
                da_stagy[var] = da_stagy[var].assign_coords(xi_rho = ('xi_rho',lons),
                                                            eta_rho = ('eta_rho', lats[1:-1]))
        da_stagy = da_stagy.drop_vars(['lat_v','lon_v'])
    else:
        for var in da_stagx:
            da_stagx[var] = da_stagx[var].assign_coords(xi_u=('xi_u',lons_u)).rename({'xi_u':'lon_u'})
        for var in da_stagy:
            da_stagy[var] = da_stagy[var].assign_coords(eta_v=('eta_v',lats_v)).rename({'eta_v':'lat_v'})
    
    da_nostagxy["xi_rho"] = ("xi_rho", lons)
    da_nostagxy["eta_rho"] = ("eta_rho", lats)
    da_nostagxy = da_nostagxy.drop_vars(['lat_rho','lon_rho'])        

    ds_croco = xr.merge([da_nostagxy,da_stagx,da_stagy],join='outer')

    ds_croco = ds_croco.rename({'eta_rho':'lat','xi_rho':'lon','s_rho':'levels'})
    ds_croco['lat'].attrs = {"units": 'degrees_north', 'axis': 'Y','long_name':'Latitude','standard_name':'latitude'}
    ds_croco['lon'].attrs = {"units": 'degrees_east', 'axis': 'X','long_name':'Longitude','standard_name':'longitude'}
    
    for var in ds_croco.data_vars:
        coords = ds_croco[var].coords
    if all(c in coords for c in ['lat', 'lon', 'time']):
        ds_croco[var].encoding['coordinates'] = 'time lat lon'

    return ds_croco

def _select_time(ds_input: xr.Dataset, dif_hours: int, sign: int) -> xr.Dataset:
    """
    Adjusts the 'XTIME' coordinate in a WRF Dataset by shifting it with a given time delta.

    Parameters
    ----------
    ds_input : xr.Dataset
        Input dataset containing the 'XTIME' variable and 'Time' dimension.

    dif_hours : int
        Number of hours to shift the time values (positive integer).

    sign : int
        Direction of the shift: use +1 to add time, -1 to subtract.

    Returns
    -------
    xr.Dataset
        Dataset with updated 'time' coordinate replacing 'XTIME'.
    """

    if 'XTIME' not in ds_input.variables or 'Time' not in ds_input.dims:
        raise KeyError("Dataset must contain 'XTIME' variable and 'Time' dimension.")

    ds_adjusted = ds_input.rename({'XTIME': 'time'}).swap_dims({'Time': 'time'})
    adjusted_time = pd.to_datetime(ds_adjusted.time.values) + pd.Timedelta(hours=sign * dif_hours)
    ds_adjusted = ds_adjusted.assign_coords(time=adjusted_time)

    return ds_adjusted

def read_wrf( file_paths: list[str], drop_vars: list[str],
    dif_hours: int = 0, sign: int = 1,
    destag: bool = True, save_path: str | None = None) -> xr.Dataset:
    """
    Reads and processes multiple WRF NetCDF output files as a single merged dataset.

    Applies optional time adjustment, destaggering, and coordinate standardization.

    Parameters
    ----------
    file_paths : list[str]
        List of paths to WRF NetCDF files (e.g., 'wrfout_d0*').

    drop_vars : list[str]
        List of variables to drop during loading.

    dif_hours : int, default=0
        Time shift (in hours) to apply to each timestep.

    sign : int, default=1
        Direction of time shift: use +1 to add or -1 to subtract.

    destag : bool, default=True
        If True, performs destaggering of staggered variables.

    save_path : str or None, default=None
        Optional path to save the final dataset as NetCDF.

    Returns
    -------
    xr.Dataset
        Combined and standardized WRF dataset.
    """
    if not file_paths:
        raise ValueError("No input files provided.")

    with xr.open_dataset(file_paths[0], engine='netcdf4') as ds_sample:
        metadata = get_metadata_vars(ds_sample, model='WRF')
        lats = ds_sample.XLAT[0, :, 0].values
        lons = ds_sample.XLONG[0, 0, :].values

        lats_v = ds_sample.XLAT_V[0, :, 0].values if not destag and 'XLAT_V' in ds_sample else None
        lons_u = ds_sample.XLONG_U[0, 0, :].values if not destag and 'XLONG_U' in ds_sample else None

    # Load and preprocess the full dataset
    ds = xr.open_mfdataset(file_paths, combine='nested', concat_dim='time',
        parallel=True, engine='netcdf4', drop_variables=drop_vars,
        preprocess=partial(_select_time, dif_hours=dif_hours, sign=sign))

    # Remove duplicate times
    _, unique_indices = np.unique(ds['time'], return_index=True)
    ds = ds.isel(time=unique_indices)

    if destag:
        ds_final = _new_wrf_coords(ds, metadata, lats, lons)
    else:
        ds_final = _new_wrf_coords(ds, metadata, lats, lons, destag=False, lats_v=lats_v, lons_u=lons_u)

    # Mark unlimited dimension
    ds_final.encoding['unlimited_dims'] = ('time',)

    if save_path:
        ds_final.to_netcdf(save_path)

    return ds_final

def read_croco(file_paths: list[str], drop_vars: list[str],
    destag: bool = True, save_path: str | None = None) -> xr.Dataset:
    """
    Reads and processes multiple CROCO NetCDF output files as a merged dataset.

    Applies optional destaggering, coordinate standardization, and conversion of model time.

    Parameters
    ----------
    file_paths : list[str]
        List of paths to CROCO NetCDF files (e.g., 'croco_avg_*.nc').

    drop_vars : list[str]
        List of variable names to drop during loading.

    destag : bool, default=True
        Whether to perform destaggering and coordinate re-alignment.

    save_path : str or None, default=None
        Optional path to save the final dataset as NetCDF.

    Returns
    -------
    xr.Dataset
        Combined and standardized CROCO dataset.
    """
    if not file_paths:
        raise ValueError("No input files provided.")

    metadata = get_metadata_vars(file_paths[0], model='CROCO', print_all=False)

    with xr.open_dataset(file_paths[0], engine='netcdf4') as ds_sample:
        lats = ds_sample.lat_rho.isel(xi_rho=0).values
        lons = ds_sample.lon_rho.isel(eta_rho=0).values

        lats_v = ds_sample.lat_v[:, 0].values if not destag and 'lat_v' in ds_sample else None
        lons_u = ds_sample.lon_u[0, :].values if not destag and 'lon_u' in ds_sample else None

    # Load and merge multiple CROCO files
    ds = xr.open_mfdataset(file_paths, combine='nested', concat_dim='time',
        parallel=True, engine='netcdf4', drop_variables=drop_vars)

    # Convert model time (seconds since 1900-01-01) to datetime
    base_time = datetime.datetime(1900, 1, 1)
    time_values = [base_time + datetime.timedelta(seconds=int(s)) for s in ds.time.values]
    ds['time'] = pd.to_datetime(time_values)

    # Remove duplicate time entries
    _, unique_indices = np.unique(ds['time'], return_index=True)
    ds = ds.isel(time=unique_indices)

    if destag:
        ds_final = _new_croco_coords(ds, metadata, lats, lons)
    else:
        ds_final = _new_croco_coords(ds, metadata, lats, lons, destag=False, lats_v=lats_v, lons_u=lons_u)

    # Mark unlimited dimension
    ds_final.encoding['unlimited_dims'] = ('time',)

    if save_path:
        ds_final.to_netcdf(save_path)

    return ds_final


