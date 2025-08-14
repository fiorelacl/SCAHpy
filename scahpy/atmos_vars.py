import numpy as np
import xarray as xr

def calc_pp(ds, vars_to_sum=['RAINC', 'RAINNC', 'RAINSH'], elim=False):
    """Calculate precipitation nominal at the output time (e.g., 3hr, etc).
    De-accumulate liquid precipitation and save it as 'PP'.

    Parameters:
    -----------
    ds : xarray.Dataset
        Dataset with the variables RAINC, RAINNC, and RAINSH already loaded and processed coordinates.
    
    vars_to_sum : list of str, optional
        List of variables to be summed for precipitation calculation (default is ['RAINC', 'RAINNC', 'RAINSH']).

    elim : bool, optional
        If True, eliminates intermediate variables after calculation (default is False).

    Returns:
    --------
    ds : xarray.Dataset
        Dataset with calculated precipitation 'PP'.

    Example:
    ---------
    # Calculate precipitation with default settings (sum of RAINC, RAINNC, and RAINSH)
    ds = calc_pp(ds)

    # Calculate precipitation using only RAINC and RAINNC
    ds = calc_pp(ds, vars_to_sum=['RAINC', 'RAINNC'])
    """
    ntime = ds.time[0:-1]
    # Calculate precipitation based on the sum of specified variables
    ds['PP2'] = sum(ds[var] for var in vars_to_sum)

    # De-accumulate precipitation and save it as 'PP'
    dd = ds['PP2'].diff('time')
    dd['time'] = ntime

    ds['PP'] = dd

        # Drop intermediate variables if elim is True
    if elim:
        df = ds.drop_vars(['PP2'] + vars_to_sum)
    else:
        df = ds.drop_vars(['PP2'])

    return df

def calc_wsp(ds,elim=False):
    """ Calculate de wind speed with zonal and meridional components (10m).
    ES: Calcula la velocidad del viento (a 10m)'

                                sqrt(u10² + v10²) = WSP

    Parameters/Parámetros:
    ----------------------
    ds : dataset with the variables U10 and V10 already loaded with 
    coordinates already processed / dataset con las variables U10 and V10 
    ya cargado con las coordenadas apropiadas.
    """

    ds['WSP']=(ds['U10']**2+ds['V10']**2)**0.5

    if elim==True:
        ds=ds.drop_vars(['U10','V10'])

    return ds

def calc_pres(ds,elim=False):
    """ Calc the atmospheric pressure and save it as 'Presion' (hPa).
    ES: Calcula la presión atmosférica y la guarda como 'Presion'.

    Parameters/Parámetros:
    ----------------------
    ds : dataset with the variables P and PB already loaded with 
    coordinates already processed / dataset con las variables P and PB
    ya cargado con las coordenadas apropiadas.
    """

    ds['Presion']=(ds['PB']+ds['P'])/100 # Divided by 100 to get hPa

    if elim==True:
        ds=ds.drop_vars(['P','PB'])

    return ds

def calc_tp(ds,elim=False):
    """ calc the potential temperature.
    ES: Calcula la temperatura potencial,con la variable T.

    Parameters/Parámetros:
    ----------------------
    ds : dataset with the variable T with coordinates already processed / 
    dataset con la variable T ya cargado con las coordenadas apropiadas.
    """

    ds['TPo']=ds['T']+300

    if elim==True:
        ds=ds.drop_vars(['T'])

    return ds

def calc_qe(ds,elim=False):
    """ calculate the specific humidity.
    ES: Calcula la humedad específica.

    Parameters/Parámetros:
    ----------------------
    ds : dataset with the variable QVAPOR already loaded with 
    coordinates already processed / dataset con las variables QVAPOR 
    ya cargado con las coordenadas apropiadas.
    """
    ds['QE']=ds['QVAPOR']/(1+ds['QVAPOR'])

    if elim==True:
        ds=ds.drop_vars(['QVAPOR'])

    return ds

def calc_celsius(ds,var):
    """ Calculate de conversion from Kelvin to Celsius'

                                K-273.15 = C

    Parameters/Parámetros:
    ----------------------
    ds : dataset with the SSTSK variable/ dataset con las variables U10 and V10 
    ya cargado con las coordenadas apropiadas.
    """

    ds[var]=ds[var]-273.15

    return ds
 
