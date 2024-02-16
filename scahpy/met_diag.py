import numpy as np
import xarray as xr

def calc_pp(ds,elim=False):
    """ de-acumulate the rainfall and save it as PP.
    ES: Calcula la precipitación nominal en el tiempo de salida (ej. 3hr, etc),
    es decir desacumula la precipitación líquida y la guarda como 'PP'.

    Parameters/Parámetros:
    ----------------------
    ds : dataset with the variables RAINC, RAINNC and RAINSH already loaded with 
    coordinates already processed / dataset con las variables RAINC, RAINNC and RAINSH 
    ya cargado con las coordenadas apropiadas.
    """
    ntime = ds.time[0:-1]
    ds['PP2'] = ds['RAINC'] + ds['RAINNC'] + ds['RAINSH']

    dd=ds['PP2'].diff('time')
    dd['time'] = ntime

    ds['PP'] = dd

    if elim==True:
        ds=ds.drop_vars(['PP2','RAINC','RAINNC','RAINSH'])
    else:
        ds=ds.drop_vars(['PP2'])

    return ds

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
 
