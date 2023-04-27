from netCDF4 import Dataset

def _list_all_WRFvars(file0):
    """Read one wrfout file and list all the variables.
    ES: Lee un archivo wrfout y lista todas las variables.
    """
    ds=Dataset(file0)
    wrf_name_vars = list(ds.variables.keys())
    return wrf_name_vars

def drop_wrf_vars(file0,sel_vars):
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

def _new_coords(file0,da,type_var):
    ds = xr.open_dataset(path0)
    if op=='surface' or op=='level':
        da = da.assign_coords({south_north=('south_north':ds.XLAT[0,:,0].values),
        west_east=('west_east':ds.XLONG[0,0,:].values)}).rename({'south_north':'lat',
        'west_east':'lon'})
    return da
