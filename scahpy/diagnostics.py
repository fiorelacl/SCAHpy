import numpy as np

def calc_pp(ds):
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
    ds['PP'] = ds['RAINC'] + ds['RAINNC'] + ds['RAINSH']

    dd=ds['PP'].diff('time')
    dd['time'] = ntime

    return dd

#def calc_t2(ds):
#    d0=0.5*(d0.resample(time='1D').min() + d0.resample(time='1D').max())
    
