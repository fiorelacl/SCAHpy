import numpy as np
import xarray as xr

def wind_speed(u: xr.DataArray, v: xr.DataArray, name: str = "WSP") -> xr.DataArray:
    """
    Compute horizontal wind speed (m s⁻¹) from zonal (U) and meridional (V) components.
    sqrt(u² + v²)

    Parameters
    ----------
    u : xr.DataArray
        Zonal wind component (m s⁻¹). Must share the same dimensions and grid as `v`.
    v : xr.DataArray
        Meridional wind component (m s⁻¹). Must share the same dimensions and grid as `u`.
    name : str, optional
        Name for the resulting DataArray. Default is "WSP".

    Returns
    -------
    xr.DataArray
        Wind speed magnitude (m s⁻¹) with CF-compliant metadata.

    """
    wsp = np.hypot(u, v)  
    wsp.name = name

    u_name = (u.name or "").upper()
    v_name = (v.name or "").upper()
    is_10m = u_name.endswith("10") and v_name.endswith("10")

    wsp.attrs.update({
        "units": "m s-1",
        "standard_name": "wind_speed",
        "long_name": "Wind speed at 10 m" if is_10m else "Wind speed",
    })
    return wsp


def pressure(p: xr.DataArray, pb: xr.DataArray, units: str = "Pa", name: str = "Pressure") -> xr.DataArray:
    """
    Compute total atmospheric pressure from perturbation (P) and base-state (PB) components.

    The WRF model outputs pressure as the sum of two fields:
    - `P`: perturbation pressure (Pa)
    - `PB`: base-state pressure (Pa)

    The total pressure is given by:
        P_total = P + PB

    Parameters
    ----------
    p : xr.DataArray
        Perturbation pressure (Pa).
    pb : xr.DataArray
        Base-state pressure (Pa).
    units : {"Pa", "hPa"}, optional
        Output units for the resulting pressure. Default is "Pa".
    name : str, optional
        Name for the resulting DataArray. Default is "Pressure".

    Returns
    -------
    xr.DataArray
        Total pressure with appropriate metadata and units.

    """
    ptot = p + pb

    units_norm = units.lower()
    if units_norm == "hpa":
        ptot = ptot / 100.0
        out_units = "hPa"
    elif units_norm == "pa":
        out_units = "Pa"
    else:
        raise ValueError("units must be 'Pa' or 'hPa'.")

    ptot.name = name
    ptot.attrs.update({
        "units": out_units,
        "long_name": "Total pressure",
        "standard_name": "air_pressure",
    })
    return ptot

def geopotential(ph: xr.DataArray, phb: xr.DataArray, name: str = "PHI") -> xr.DataArray:
    """
    Compute total geopotential (Φ) from perturbation and base-state components.

    The WRF model provides geopotential in two parts:
    - PH  : perturbation geopotential (m² s⁻²)
    - PHB : base-state geopotential (m² s⁻²)

    The total geopotential is given by:
        Φ = PH + PHB

    Parameters
    ----------
    ph : xr.DataArray
        Perturbation geopotential (m² s⁻²).
    phb : xr.DataArray
        Base-state geopotential (m² s⁻²).
    name : str, optional
        Name for the resulting DataArray. Default is "PHI".

    Returns
    -------
    xr.DataArray
        Total geopotential (m² s⁻²).
    """
    phi = ph + phb
    phi.name = name
    phi.attrs.update({
        "units": "m^2 s^-2",
        "long_name": "Total geopotential",
        "standard_name": "geopotential"
    })
    return phi

def geop_height(ph: xr.DataArray, phb: xr.DataArray, units: str = "m", name: str = "Z") -> xr.DataArray:
    """
    Compute geopotential height (Z) from total geopotential divided by gravity.

    The WRF model defines:
        Z = (PH + PHB) / g

    where g = 9.81 m s⁻².

    Parameters
    ----------
    ph : xr.DataArray
        Perturbation geopotential (m² s⁻²).
    phb : xr.DataArray
        Base-state geopotential (m² s⁻²).
    units : {"m", "km"}, optional
        Output units. Default is meters ("m").
    name : str, optional
        Name for the resulting DataArray. Default is "Z".

    Returns
    -------
    xr.DataArray
        Geopotential height (m or km above sea level).
    """
    g = 9.81
    z = (ph + phb) / g

    if units.lower() == "km":
        z = z / 1000.0
        out_units = "km"
        long_name = "Geopotential height (km a.s.l.)"
    elif units.lower() == "m":
        out_units = "m"
        long_name = "Geopotential height (m a.s.l.)"
    else:
        raise ValueError("units must be 'm' or 'km'.")

    z.name = name
    z.attrs.update({
        "units": out_units,
        "long_name": long_name,
        "standard_name": "geopotential_height"
    })
    return z

def t_pot(Tpert: xr.DataArray, celsius: bool = False, name: str = "theta") -> xr.DataArray:
    """
    Compute potential temperature (θ) from the WRF perturbation potential temperature.

    In WRF outputs:
        θ = T + 300

    Parameters
    ----------
    Tpert : xr.DataArray
        Perturbation potential temperature (K).
    celsius : bool, optional
        If True, convert from Kelvin to Celsius. Default is False.
    name : str, optional
        Name for the resulting DataArray. Default is "theta".

    Returns
    -------
    xr.DataArray
        Potential temperature (K or °C depending on `celsius` flag).
    """
    theta = Tpert + 300.0
    if celsius:
        theta = theta - 273.15
        units = "°C"
    else:
        units = "K"

    theta.name = name
    theta.attrs.update({
        "units": units,
        "long_name": "Potential temperature",
        "standard_name": "air_potential_temperature"
    })
    return theta

def t_air(
    Tpert: xr.DataArray,
    P: xr.DataArray,
    PB: xr.DataArray,
    *,
    celsius: bool = False
) -> xr.DataArray:
    """
    Compute absolute air temperature (T_air) from perturbation potential temperature (T)
    and total pressure using the Poisson equation.

        θ = T + 300
        T_air = θ * (p / 1000) ** κ

    where:
        κ = 0.286  (R_d / c_p)

    Parameters
    ----------
    Tpert : xr.DataArray
        Perturbation potential temperature (K) from WRF output variable "T".
    P : xr.DataArray
        Perturbation pressure (Pa) from WRF output variable "P".
    PB : xr.DataArray
        Base-state pressure (Pa) from WRF output variable "PB".
    celsius : bool, optional
        If True, convert air temperature from Kelvin to Celsius. Default is False.

    Returns
    -------
    xr.DataArray
        Absolute air temperature (K or °C), with CF-compliant metadata.

    """

    p_hpa = (P + PB) / 100.0
    theta = Tpert + 300.0

    kappa = 0.286
    T_air = theta * (p_hpa / 1000.0) ** kappa

    if celsius:
        T_air = T_air - 273.15
        units = "°C"
    else:
        units = "K"

    T_air.name = "T_air"
    T_air.attrs.update({
        "units": units,
        "long_name": "Air temperature",
        "standard_name": "air_temperature"
    })
    return T_air

def rh(
    Tpert: xr.DataArray,
    P: xr.DataArray,
    PB: xr.DataArray,
    QVAPOR: xr.DataArray,
    *,
    clip: bool = True
) -> xr.DataArray:
    """
    Compute relative humidity (%) from perturbation temperature (T),
    pressure components (P, PB), and specific humidity (QVAPOR).

    Internally, the function calls `t_air()` to compute the absolute air
    temperature and then applies a Bolton-type formulation for saturation
    vapor pressure over water:

        e_s(hPa) = 6.112 * exp(17.67 * (T - 273.15) / (T - 29.65))
        e(hPa)   = qv * p(hPa) / (0.622 + qv)
        RH(%)    = 100 * e / e_s

    Parameters
    ----------
    Tpert : xr.DataArray
        Perturbation potential temperature (K) from WRF output variable "T".
    P : xr.DataArray
        Perturbation pressure (Pa) from WRF output variable "P".
    PB : xr.DataArray
        Base-state pressure (Pa) from WRF output variable "PB".
    QVAPOR : xr.DataArray
        Water vapor mixing ratio (kg kg⁻¹) from WRF output variable "QVAPOR".
    clip : bool, optional
        If True (default), clip RH to [0, 100] %.

    Returns
    -------
    xr.DataArray
        Relative humidity in percent (%), with CF-compliant metadata.

    """
    T_air = t_air(Tpert, P, PB, celsius=False)
    p_hpa = (P + PB) / 100.0

    e = QVAPOR * p_hpa / (0.622 + QVAPOR)
    es = 6.112 * np.exp((17.67 * (T_air - 273.15)) / (T_air - 29.65))

    RH = 100.0 * (e / es)

    if clip:
        RH = RH.clip(min=0, max=100)

    RH.name = "RH"
    RH.attrs.update({
        "units": "%",
        "long_name": "Relative humidity",
        "standard_name": "relative_humidity"
    })
    return RH

