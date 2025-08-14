import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfe
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from cartopy.io.shapereader import Reader
import cmocean
import matplotlib.colors
import importlib.resources
from pathlib import Path

def map_pp_uv10_sst(pp, sfc, levs, levs2, sst_var='SSTSK', shapefile=None, output_path=None, save_maps=True, freq=None,
                    quiverkey_speed=5, extent=None):
    """
    Plots precipitation maps for specified months.

    Parameters:
    - pp (xarray.Dataset): Precipitation data.
    - sfc (xarray.Dataset): Surface data with SST and UV10 data.
    - levs (list): Contour levels for precipitation.
    - levs2 (list): Contour levels for SSTSK.
    - sst_var (str): Name of the variable for SST in the sfc dataset. Defaults to 'SSTSK'.
    - shapefile (str): Path to the shapefile for South America countries (could be any other).
    - output_path (str, optional): Path to save the maps. If None, maps will be displayed but not saved. Defaults to None.
    - freq (str): Could be 'H' , 'D', 'M', 'Y'. Defaults to Hourly ('H').
    - save_maps (bool, optional): If True, saves the maps. If False, only displays them. Defaults to True.
    - quiverkey_speed (int, optional): Speed parameter for quiverkey. Defaults to 5.
    - extent: [x1,x2,y1,y2] spatial extension
    """
    if shapefile is None:
        data_dir = importlib.resources.files('scahpy.data')
        data_path = Path(data_dir, 'SA_paises.shp')
        sa = cfe.ShapelyFeature(Reader(data_path).geometries(), ccrs.PlateCarree(), edgecolor='k', facecolor='none')
    else:
        sa = cfe.ShapelyFeature(Reader(shapefile).geometries(), ccrs.PlateCarree(), edgecolor='k', facecolor='none')

    if extent is None:
        extent = [-93.8, -68, -21.9, 4.1]

    cmaps = cmocean.tools.lighten(cmocean.cm.rain, 0.85)
    norm = matplotlib.colors.BoundaryNorm(levs, cmaps.N)

    lons = pp.lon.values
    lats = pp.lat.values
    times = np.datetime_as_string(sfc.time.values, unit='m')

    for i in range(len(times)):
        if freq == 'H' or freq is None:
            timess = times[i][0:13]
        elif freq == 'D':
            timess = times[i][0:10]
        elif freq == 'M':
            timess = times[i][0:7]
        elif freq == 'Y':
            timess = times[i][0:4]

        fig, axs = plt.subplots(figsize=(13, 12), ncols=1, nrows=1, sharex=True, sharey=True,
                                subplot_kw=dict(projection=ccrs.PlateCarree()))

        pcm = axs.contourf(lons, lats, pp.sel(time=timess), levels=levs,
                           cmap=cmaps, norm=norm, extend='both', transform=ccrs.PlateCarree())
        fig.colorbar(pcm, ax=axs, label='mm', orientation='vertical', shrink=.7, pad=0.07, aspect=20, format='%3.0f')
        c = axs.contour(lons, lats, sfc[sst_var].sel(time=timess),
                        levels=levs2, colors=['#F29727', '#C70039', '#511F73'],
                        linewidths=[1.5, 1.6, 1.8], linestyles='solid',
                        alpha=0.45, transform=ccrs.PlateCarree(), zorder=7)
        axs.clabel(c, levels=levs2, inline=False, colors='#000000', fontsize=12, zorder=9)
        Q = axs.quiver(lons[::7], lats[::7],
                       sfc.U10.sel(time=timess)[::7, ::7], sfc.V10.sel(time=timess)[::7, ::7],
                       headwidth=5, headlength=7)
        axs.quiverkey(Q, 0.87, 1.02, quiverkey_speed, f'{quiverkey_speed} m/s', labelpos='E', coordinates='axes', labelsep=0.05)

        axs.add_feature(sa, linewidth=0.7, zorder=7)
        lon_formatter = LongitudeFormatter()
        lat_formatter = LatitudeFormatter()
        axs.yaxis.set_major_formatter(lat_formatter)
        axs.xaxis.set_major_formatter(lon_formatter)
        axs.set_extent(extent)

        plt.title(f'Map of Precipitation : {timess}')

        if save_maps:
            if output_path is None:
                raise ValueError("Output path cannot be None when saving maps.")
            plt.savefig(f'{output_path}/m_TSM_UV_PP_{timess}.png',
                        bbox_inches='tight', dpi=300, facecolor='white', transparent=False)
        else:
            plt.show()

        plt.close()

def map_clim_pp_uv10_sst(pp, sfc, levs, levs2, shapefile, sst_var='SSTSK', output_path=None, month_list=None,
                         save_maps=True, quiverkey_speed=5, extent=None):
    """
    Plots precipitation maps for specified months.

    Parameters:
    - pp (xarray.Dataset): Precipitation data.
    - sfc (xarray.Dataset): Surface data with SST and UV10 data.
    - levs (list): Contour levels for precipitation.
    - levs2 (list): Contour levels for SST.
    - sst_var (str): Name of the variable for SST in the sfc dataset. Defaults to 'SSTSK'.
    - shapefile (str): Path to the shapefile for South America countries (could be any other).
    - output_path (str, optional): Path to save the maps. If None, maps will be displayed but not saved. Defaults to None.
    - month_list (list, optional): List of months to plot. Defaults to None (all months).
    - save_maps (bool, optional): If True, saves the maps. If False, only displays them. Defaults to True.
    - quiverkey_speed (int, optional): Speed parameter for quiverkey. Defaults to 5.
    - extent: [x1,x2,y1,y2] spatial extension
    """
    if shapefile is None:
        data_dir = importlib.resources.files('scahpy.data')
        data_path = Path(data_dir, 'SA_paises.shp')
        sa = cfe.ShapelyFeature(Reader(data_path).geometries(), ccrs.PlateCarree(), edgecolor='k', facecolor='none')
    else:
        sa = cfe.ShapelyFeature(Reader(shapefile).geometries(), ccrs.PlateCarree(), edgecolor='k', facecolor='none')

    if extent is None:
        extent = [-93.8, -68, -21.9, 4.1]

    cmaps = cmocean.tools.lighten(cmocean.cm.rain, 0.85)
    norm = matplotlib.colors.BoundaryNorm(levs, cmaps.N)

    lons = pp.lon.values
    lats = pp.lat.values

    if month_list is None:
        month_list = range(1, 13)

    for month in month_list:
        fig, axs = plt.subplots(figsize=(13, 12), ncols=1, nrows=1, sharex=True, sharey=True,
                                subplot_kw=dict(projection=ccrs.PlateCarree()))

        pcm = axs.contourf(lons, lats, pp.sel(month=month), levels=levs,
                           cmap=cmaps, norm=norm, extend='both', transform=ccrs.PlateCarree())
        fig.colorbar(pcm, ax=axs, label='mm/month', orientation='vertical', shrink=.7, pad=0.07, aspect=20, format='%3.0f')
        c = axs.contour(lons, lats, sfc[sst_var].sel(month=month),
                        levels=levs2, colors=['#F29727', '#C70039', '#511F73'],
                        linewidths=[1.5, 1.6, 1.8], linestyles='solid',
                        alpha=0.45, transform=ccrs.PlateCarree(), zorder=7)
        axs.clabel(c, levels=levs2, inline=False, colors='#000000', fontsize=12, zorder=9)
        Q = axs.quiver(lons[::7], lats[::7],
                       sfc.U10.sel(month=month)[::7, ::7], sfc.V10.sel(month=month)[::7, ::7],
                       headwidth=5, headlength=7)
        axs.quiverkey(Q, 0.87, 1.02, quiverkey_speed, f'{quiverkey_speed} m/s', labelpos='E', coordinates='axes', labelsep=0.05)

        axs.add_feature(sa, linewidth=0.7, zorder=7)
        lon_formatter = LongitudeFormatter()
        lat_formatter = LatitudeFormatter()
        axs.yaxis.set_major_formatter(lat_formatter)
        axs.xaxis.set_major_formatter(lon_formatter)
        axs.set_extent(extent)

        plt.title(f'Map of Precipitation Month: {month:02d}')

        if save_maps:
            if output_path is None:
                raise ValueError("Output path cannot be None when saving maps.")
            plt.savefig(f'{output_path}/m_TSM_UV_PP_{month}.png',
                        bbox_inches='tight', dpi=300, facecolor='white', transparent=False)
        else:
            plt.show()

        plt.close()

def cross_section_yz(ds,vari,levs,cmaps,title,quiverkey_speed=5,
                     output_path=None, freq=None, save_maps=True):
    """
    Plots Cross Sections of Pressure level variables in YZ direction.

    Parameters:
    - ds (xarray.Dataset): wrfout data already interpolated to pressure levels (output from spatial_scales.vert_levs()).
    - vari (list): List of variables to plot including V and W.
    - levs (list): Contour levels for variable.
    - title (str): Title to display in the graph.
    - output_path (str, optional): Path to save the maps. If None, maps will be displayed but not saved. Defaults to None.
    - freq (str): Could be 'H' , 'D', 'M', 'Y'. Defaults to Hourly ('H').
    - save_maps (bool, optional): If True, saves the maps. If False, only displays them. Defaults to True.
    - quiverkey_speed (int, optional): Speed parameter for quiverkey. Defaults to 5.
    """

    lats = ds.lat.values
    times = np.datetime_as_string(ds.time.values,unit='m')
    Y=ds.level.values
    
    norms = matplotlib.colors.BoundaryNorm(levs, cmaps.N)
    plt.rcParams['font.family'] = 'Monospace'

    if freq == 'H' or freq is None:
        j=13
    elif freq == 'D':
        j=10
    elif freq == 'M':
        j=7
    elif freq == 'Y':
        j=4   
    
    for i in range(len(times)):
            
        timess = times[i][0:j]
        
        vv=ds.get('V').sel(time=timess)
        ww=ds.get('W').sel(time=timess)*1000
        var=ds.get(vari).sel(time=timess) #(g/kg)
        
        fig,axs = plt.subplots(figsize=(6,10),ncols=1,nrows=1)
        pcm=axs.contourf(lats, Y, var,levels=levs,cmap=cmaps,norm=norms,extend='both')
        fig.colorbar(pcm,ax=axs,label='', orientation='horizontal', shrink=.9,pad=0.04,aspect=25,format='%3.1f')
        Q=axs.quiver(lats[::4],Y,vv[::,::4],ww[::,::4],scale=170,headwidth=4,headlength=4)
        axs.invert_yaxis()
        axs.quiverkey(Q,0.87,0.98,quiverkey_speed, f'{quiverkey_speed} m/s',labelpos='E',coordinates='axes',labelsep=0.05) 
        plt.title(f'{title} {timess}',loc='center')
    
        if save_maps:
            if output_path is None:
                raise ValueError("Output path cannot be None when saving maps.")
            plt.savefig(f'{output_path}/Cross_Section_YZ_{var}_{timess}.png',
                        bbox_inches='tight', dpi=300, facecolor='white', transparent=False)
        else:
            plt.show()

        plt.close()

def cross_section_xz(ds,vari,levs,cmaps,title,quiverkey_speed=5,
                     output_path=None, freq=None, save_maps=True):
    """
    Plots Cross Sections of Pressure level variables in XZ direction.

    Parameters:
    - ds (xarray.Dataset): wrfout data already interpolated to pressure levels (output from spatial_scales.vert_levs()).
    - vari (list): List of variables to plot including V and W.
    - levs (list): Contour levels for variable.
    - title (str): Title to display in the graph.
    - output_path (str, optional): Path to save the maps. If None, maps will be displayed but not saved. Defaults to None.
    - freq (str): Could be 'H' , 'D', 'M', 'Y'. Defaults to Hourly ('H').
    - save_maps (bool, optional): If True, saves the maps. If False, only displays them. Defaults to True.
    - quiverkey_speed (int, optional): Speed parameter for quiverkey. Defaults to 5.
    """

    lons = ds.lon.values
    times = np.datetime_as_string(ds.time.values,unit='m')
    Y=ds.level.values
    
    norms = matplotlib.colors.BoundaryNorm(levs, cmaps.N)
    plt.rcParams['font.family'] = 'Monospace'

    if freq == 'H' or freq is None:
        j=13
    elif freq == 'D':
        j=10
    elif freq == 'M':
        j=7
    elif freq == 'Y':
        j=4   
    
    for i in range(len(times)):
            
        timess = times[i][0:j]
        
        uu=ds.get('U').sel(time=timess)
        ww=ds.get('W').sel(time=timess)*1000
        var=ds.get(vari).sel(time=timess) #(g/kg)
        
        fig,axs = plt.subplots(figsize=(6,10),ncols=1,nrows=1)
        pcm=axs.contourf(lons, Y, var,levels=levs,cmap=cmaps,norm=norms,extend='both')
        fig.colorbar(pcm,ax=axs,label='', orientation='horizontal', shrink=.9,pad=0.04,aspect=25,format='%3.1f')
        Q=axs.quiver(lons[::4],Y,uu[::,::4],ww[::,::4],scale=170,headwidth=4,headlength=4)
        axs.invert_yaxis()
        axs.quiverkey(Q,0.87,0.98,quiverkey_speed, f'{quiverkey_speed} m/s',labelpos='E',coordinates='axes',labelsep=0.05) 
        plt.title(f'{title} {timess}',loc='center')
    
        if save_maps:
            if output_path is None:
                raise ValueError("Output path cannot be None when saving maps.")
            plt.savefig(f'{output_path}/Cross_Section_XZ_{var}_{timess}.png',
                        bbox_inches='tight', dpi=300, facecolor='white', transparent=False)
        else:
            plt.show()

        plt.close()

def series_obs_diag(obs, wrf, obs_var, wrf_var, lat_min, lat_max, lon_min, lon_max,
                    obs_color='black', obs_linewidth=1.7, obs_linestyle='-', obs_label='OBS',
                    wrf_color='#66A61E', wrf_linewidth=1.7, wrf_linestyle=':', wrf_label='IGP-RESM-COW',
                    save_path=None):
    plt.rcParams['font.family'] = 'Monospace'
    fig, axs = plt.subplots(figsize=(18, 6), ncols=1, nrows=1)
    
    obs[obs_var].sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max)).mean(dim='lat', skipna=True).mean(dim='lon', skipna=True).plot(
        x='time', color=obs_color, linewidth=obs_linewidth, linestyle=obs_linestyle, label=obs_label, zorder=10)
    
    wrf[wrf_var].sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max)).mean(dim='lat', skipna=True).mean(dim='lon', skipna=True).plot(
        x='time', color=wrf_color, linewidth=wrf_linewidth, linestyle=wrf_linestyle, label=wrf_label, zorder=20)
    
    plt.legend(loc="upper right")
    
    if save_path:
        plt.savefig(save_path)
        print(f"Image saved to {save_path}")
    
    plt.show()

def plot_perfil_2vars(dataset, lat, lon, tiempo, var1, var2, guardar=False, nombre_archivo="perfil_combinado.png", titulo_personalizado=None):
    """ Genera un gráfico combinado de dos variables seleccionadas en un mismo eje para un punto y tiempo específico.
        Permite guardar el gráfico como archivo y define dinámicamente si los niveles son 'levels' o 'zlevels'.

        Args:
            dataset (xarray.Dataset): Dataset con las variables.
            lat (float): Latitud del punto de interés.
            lon (float): Longitud del punto de interés.
            tiempo (str): Tiempo de interés (formato ISO 8601).
            var1 (str): Primera variable para graficar.
            var2 (str): Segunda variable para graficar.
            guardar (bool): Si es True, guarda el gráfico en un archivo.
            nombre_archivo (str): Nombre del archivo para guardar el gráfico.
            titulo_personalizado (str): Título personalizado del gráfico.
    """
    # Verificar si el dataset tiene 'levels' o 'zlevels' como coordenada de profundidad
    if 'levels' in dataset.coords:
        niveles = dataset['levels']
        etiqueta_niveles = 'Niveles Sigma'
    elif 'zlevel' in dataset.coords:
        niveles = dataset['zlevel']
        etiqueta_niveles = 'Profundidad (m)'
    else:
        raise ValueError("El dataset no contiene coordenadas 'levels' ni 'zlevel'.")

    # Extraer datos en el punto y tiempo seleccionados
    datos_var1 = dataset[var1].sel(lat=lat, lon=lon, time=tiempo, method='nearest')
    datos_var2 = dataset[var2].sel(lat=lat, lon=lon, time=tiempo, method='nearest')

    # Crear el gráfico combinado
    fig, ax1 = plt.subplots(figsize=(6, 8))

    # Gráfico de la primera variable
    ax1.plot(datos_var1, niveles, label=f'{var1}', color='red')
    ax1.set_xlabel(f'{var1}', color='red')
    ax1.set_ylabel(etiqueta_niveles)
    ax1.tick_params(axis='x', colors='red')

    # Crear un segundo eje para la segunda variable
    ax2 = ax1.twiny()
    ax2.plot(datos_var2, niveles, label=f'{var2}', color='blue')
    ax2.set_xlabel(f'{var2}', color='blue')
    ax2.tick_params(axis='x', colors='blue')

    # Título del gráfico
    if titulo_personalizado:
        plt.title(titulo_personalizado)
    else:
        plt.title(f'Perfil Combinado de {var1} y {var2}\nLat: {lat}, Lon: {lon}, Tiempo: {str(tiempo)}')

    plt.grid()

    # Guardar el gráfico si se especifica
    if guardar:
        plt.savefig(nombre_archivo, dpi=300)
        print(f"Gráfico guardado como: {nombre_archivo}")
    
    # Mostrar el gráfico
    plt.show()   

def plot_ts(dataset, lat, lon, tiempo, variable_color='levels', guardar=False, nombre_archivo="grafico_ts.png"):
    """
    Genera un gráfico T-S (Temperatura-Salinidad) donde los puntos se colorean según una variable definida.

    Args:
        dataset (xarray.Dataset): Dataset con las variables.
        lat (float): Latitud del punto de interés.
        lon (float): Longitud del punto de interés.
        tiempo (str): Tiempo de interés (formato ISO 8601).
        variable_color (str): Nombre de la variable para colorear los puntos (por defecto, 'levels').
        guardar (bool): Si es True, guarda el gráfico en un archivo.
        nombre_archivo (str): Nombre del archivo para guardar el gráfico.
    """
    # Verificar que las variables necesarias existan en el dataset
    if 'temp' not in dataset.data_vars or 'salt' not in dataset.data_vars:
        raise ValueError("El dataset debe contener las variables 'temp' y 'salt'.")
    
    if variable_color not in dataset:
        raise ValueError(f"La variable '{variable_color}' no se encuentra en el dataset.")

    # Extraer datos en el punto y tiempo seleccionados
    temp = dataset['temp'].sel(lat=lat, lon=lon, time=tiempo, method='nearest')
    salt = dataset['salt'].sel(lat=lat, lon=lon, time=tiempo, method='nearest')
    color_data = dataset[variable_color].values

    # Aplanar los datos para graficar
    temp_flat = temp.values.flatten()
    salt_flat = salt.values.flatten()
    color_flat = color_data.flatten()

    # Crear el gráfico T-S
    plt.figure(figsize=(8, 6))
    sc = plt.scatter(temp_flat, salt_flat, c=color_flat, cmap='viridis', edgecolor='k', s=50)
    plt.colorbar(sc, label=variable_color.capitalize())
    plt.xlabel('Temperatura (°C)')
    plt.ylabel('Salinidad (PSU)')
    plt.title(f'Gráfico T-S\nLat: {lat}, Lon: {lon}, Tiempo: {str(tiempo)}')
    plt.grid()

    # Guardar el gráfico si se especifica
    if guardar:
        plt.savefig(nombre_archivo, dpi=300)
        print(f"Gráfico guardado como: {nombre_archivo}")
    
    # Mostrar el gráfico
    plt.show()

def plot_xz(dataset, lat, variable, tiempo, niveles_contorno=None, guardar=False, nombre_archivo="plot_xz.png"):
    """
    Genera una sección vertical (latitud fija) de una variable en el plano XZ con zona continental pintada en marrón.

    Args:
        dataset (xarray.Dataset): Dataset con las variables.
        lat (float): Valor fijo de latitud para la sección.
        variable (str): Nombre de la variable a graficar.
        tiempo (str): Tiempo específico para seleccionar los datos (formato ISO 8601).
        niveles_contorno (list): Lista de niveles para los contornos.
        guardar (bool): Si es True, guarda el gráfico en un archivo.
        nombre_archivo (str): Nombre del archivo para guardar el gráfico.
    """
    # Verificar que la variable exista en el dataset
    if variable not in dataset.data_vars:
        raise ValueError(f"La variable '{variable}' no se encuentra en el dataset.")
    
    # Seleccionar la sección (latitud fija y tiempo)
    seccion = dataset[variable].sel(lat=lat, time=tiempo, method='nearest')
    x = dataset['lon'].values  # Coordenadas de longitud
    z = dataset['levels'].values if 'levels' in dataset.coords else dataset['zlevel'].values  # Coordenadas de profundidad

    # Crear el gráfico
    plt.figure(figsize=(10, 6))
    contorno = plt.contourf(x, z, seccion, levels=niveles_contorno, cmap='viridis', extend='both')
    plt.colorbar(contorno, label=f'{variable}')
    contornos_linea = plt.contour(x, z, seccion, levels=niveles_contorno, colors='black', linewidths=0.5)
    plt.clabel(contornos_linea, inline=True, fontsize=8)


    # Configuración del gráfico
    plt.xlabel('Longitud (°)')
    plt.ylabel('Profundidad (m)')
    plt.title(f'Sección {variable} a Latitud: {lat}, Tiempo: {tiempo}')

    # Guardar el gráfico si se especifica
    if guardar:
        plt.savefig(nombre_archivo, dpi=300)
        print(f"Gráfico guardado como: {nombre_archivo}")
    
    # Mostrar el gráfico
    plt.show()


def plot_yz(dataset, lon, variable, tiempo, niveles_contorno=None, guardar=False, nombre_archivo="plot_yz.png"):
    """
    Genera una sección vertical (longitud fija) de una variable en el plano YZ con zona continental pintada en marrón.

    Args:
        dataset (xarray.Dataset): Dataset con las variables.
        lon (float): Valor fijo de longitud para la sección.
        variable (str): Nombre de la variable a graficar.
        tiempo (str): Tiempo específico para seleccionar los datos (formato ISO 8601).
        niveles_contorno (list): Lista de niveles para los contornos.
        guardar (bool): Si es True, guarda el gráfico en un archivo.
        nombre_archivo (str): Nombre del archivo para guardar el gráfico.
    """
    # Verificar que la variable exista en el dataset
    if variable not in dataset.data_vars:
        raise ValueError(f"La variable '{variable}' no se encuentra en el dataset.")
    
    # Seleccionar la sección (longitud fija y tiempo)
    seccion = dataset[variable].sel(lon=lon, time=tiempo, method='nearest')
    y = dataset['lat'].values  # Coordenadas de latitud
    z = dataset['levels'].values if 'levels' in dataset.coords else dataset['zlevel'].values  # Coordenadas de profundidad

    # Crear el gráfico
    plt.figure(figsize=(10, 6))
    contorno = plt.contourf(y, z, seccion, levels=niveles_contorno, cmap='viridis', extend='both')
    plt.colorbar(contorno, label=f'{variable}')
    contornos_linea = plt.contour(y, z, seccion, levels=niveles_contorno, colors='black', linewidths=0.5)
    plt.clabel(contornos_linea, inline=True, fontsize=8)

    # Configuración del gráfico
    plt.xlabel('Latitud (°)')
    plt.ylabel('Profundidad (m)')
    plt.title(f'Sección {variable} a Longitud: {lon}, Tiempo: {tiempo}')

    # Guardar el gráfico si se especifica
    if guardar:
        plt.savefig(nombre_archivo, dpi=300)
        print(f"Gráfico guardado como: {nombre_archivo}")
    
    # Mostrar el gráfico
    plt.show()