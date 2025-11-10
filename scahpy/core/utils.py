import numpy as np
import xarray as xr


def to_celsius(temp):
    """
    Convert temperature from Kelvin to Celsius.

    Parameters
    ----------
    temp : float | np.ndarray | xr.DataArray
        Temperature in Kelvin.

    Returns
    -------
    float | np.ndarray | xr.DataArray
        Temperature in Celsius, preserving attributes if input is DataArray.
    """
    result = temp - 273.15

    if isinstance(temp, xr.DataArray):
        out = result
        out.attrs = temp.attrs.copy()
        out.attrs.update({"units": "°C", "description": "Temperature in Celsius"})
        return out
    else:
        return result


def to_kelvin(temp):
    """
    Convert temperature from Celsius to Kelvin.
    
    Parameters
    ----------
    temp : float | np.ndarray | xr.DataArray
        Temperature in Celsius.

    Returns
    -------
    float | np.ndarray | xr.DataArray
        Temperature in Kelvin, preserving attributes if input is DataArray.
    """
    result = temp + 273.15

    if isinstance(temp, xr.DataArray):
        out = result
        out.attrs = temp.attrs.copy()
        out.attrs.update({"units": "K", "description": "Temperature in Kelvin"})
        return out
    else:
        return result


def to_hpa(pres):
    """
    Convert pressure from Pascals (Pa) to hectoPascals (hPa).
    
    Parameters
    ----------
    pres : float | np.ndarray | xr.DataArray
        Pressure in Pascals.

    Returns
    -------
    float | np.ndarray | xr.DataArray
        Pressure in hectoPascals, preserving attributes if input is DataArray.

    """
    result = pres / 100.0

    if isinstance(pres, xr.DataArray):
        out = result
        out.attrs = pres.attrs.copy()
        out.attrs.update({"units": "hPa", "description": "Pressure in hPa"})
        return out
    else:
        return result


def to_pa(pres):
    """
    Convert pressure from hectoPascals (hPa) to Pascals (Pa).

    Parameters
    ----------
    pres : float | np.ndarray | xr.DataArray
        Pressure in hectoPascals.

    Returns
    -------
    float | np.ndarray | xr.DataArray
        Pressure in Pascals, preserving attributes if input is DataArray.
    """
    result = pres * 100.0

    if isinstance(pres, xr.DataArray):
        out = result
        out.attrs = pres.attrs.copy()
        out.attrs.update({"units": "Pa", "description": "Pressure in Pa"})
        return out
    else:
        return result

def central_diff(da: xr.DataArray, dim: str) -> xr.DataArray:
    """
    Compute the centered finite difference along a given dimension.

    This returns the simple centered stencil (f[i+1] - f[i-1]) / 2, i.e.
    without dividing by the grid spacing. The caller can later scale by
    metric coefficients (e.g., pm = 1/Δx, pn = 1/Δy).

    Edge handling:
        The first and last points along `dim` are set to NaN because a
        centered derivative is not defined there (missing neighbors).
        Coordinates are preserved; only data values at the edges become NaN.

    Parameters
    ----------
    da : xr.DataArray
        Input array. Must contain dimension `dim`.
    dim : str
        Name of the dimension along which to compute the derivative.

    Returns
    -------
    xr.DataArray
        Centered difference with the same dimensions and coordinates as `da`,
        except that the two edge points along `dim` are NaN. Variable name and
        attributes are preserved.
    """
    if dim not in da.dims:
        raise ValueError(f"Dimension '{dim}' not present in DataArray: {list(da.dims)}")

    fwd = da.shift({dim: -1})
    bwd = da.shift({dim:  1})
    out = 0.5 * (fwd - bwd)

    out = out.where(~(fwd.isnull() | bwd.isnull()))

    out = out.transpose(*da.dims)
    out.name = getattr(da, "name", None)
    out.attrs = da.attrs.copy()
    return out


def ddx(field: xr.DataArray, metric_x: xr.DataArray | float, *, x_dim: str = "x") -> xr.DataArray:
    """
    Compute the partial derivative ∂(field)/∂x using a provided grid metric.

    Parameters
    ----------
    field : xr.DataArray
        Input variable defined on a rectilinear or curvilinear grid.
    metric_x : xr.DataArray or float
        Grid metric in the x-direction (typically 1/Δx).
        For CROCO/ROMS, this corresponds to `pm`; for WRF, to `mapfac_m / dx`.
    x_dim : str, optional
        Name of the x dimension. Default is "x".

    Returns
    -------
    xr.DataArray
        Zonal derivative scaled by the x-direction metric.
    """
    return metric_x * central_diff(field, x_dim)


def ddy(field: xr.DataArray, metric_y: xr.DataArray | float, *, y_dim: str = "y") -> xr.DataArray:
    """
    Compute the partial derivative ∂(field)/∂y using a provided grid metric.

    Parameters
    ----------
    field : xr.DataArray
        Input variable defined on a rectilinear or curvilinear grid.
    metric_y : xr.DataArray or float
        Grid metric in the y-direction (typically 1/Δy).
        For CROCO/ROMS, this corresponds to `pn`; for WRF, to `mapfac_n / dy`.
    y_dim : str, optional
        Name of the y dimension. Default is "y".

    Returns
    -------
    xr.DataArray
        Meridional derivative scaled by the y-direction metric.
    """
    return metric_y * central_diff(field, y_dim)


def rotate_to_EN(
    u: xr.DataArray,
    v: xr.DataArray,
    *,
    angle: xr.DataArray | None = None,
    cosang: xr.DataArray | None = None,
    sinang: xr.DataArray | None = None,
) -> tuple[xr.DataArray, xr.DataArray]:
    """
    Rotate horizontal velocity components from grid-relative to
    East–North coordinates.

    Parameters
    ----------
    u, v : xr.DataArray
        Zonal and meridional components on the model grid.
    angle : xr.DataArray, optional
        Grid orientation angle in radians (used in CROCO/ROMS).
    cosang, sinang : xr.DataArray, optional
        Cosine and sine of the grid angle (used in WRF).

    Returns
    -------
    (u_east, v_north) : tuple of xr.DataArray
        Velocity components rotated into true east–north coordinates.
    """
    if angle is not None:
        cosang, sinang = np.cos(angle), np.sin(angle)
    if cosang is None or sinang is None:
        raise ValueError("Either `angle` or both `cosang` and `sinang` must be provided.")
    u_east = u * cosang - v * sinang
    v_north = u * sinang + v * cosang
    u_east.attrs = u.attrs.copy(); v_north.attrs = v.attrs.copy()
    return u_east, v_north


def apply_mask(
    da: xr.DataArray,
    mask: xr.DataArray,
    *,
    sea_is_one: bool = True,
    lakemask: xr.DataArray | None = None,
    exclude_lakes: bool = True,
) -> xr.DataArray:
    """
    Apply a land–sea (and optionally lake) mask to the input variable.

    Parameters
    ----------
    da : xr.DataArray
        Variable to which the mask is applied.
    mask : xr.DataArray
        Land–sea mask. May follow either convention:
        - CROCO/ROMS: 1 = ocean, 0 = land
        - WRF:       1 = land, 0 = ocean
    sea_is_one : bool, optional
        True  →  mask==1 means ocean (ROMS style).
        False →  mask==1 means land  (WRF style).
    lakemask : xr.DataArray, optional
        Lake mask (1 = lake, 0 = not lake). If provided and
        ``exclude_lakes=True``, those points will be masked (set to NaN).
    exclude_lakes : bool, optional
        If True and `lakemask` is available, mask out lakes as well.

    Returns
    -------
    xr.DataArray
        Masked variable with non-ocean values set to NaN.
    """
    m = mask.astype(bool)

    # If WRF (1 = land, 0 = ocean)
    if not sea_is_one:
        m = ~m  # ocean → True, land → False

    if exclude_lakes and (lakemask is not None):
        lake = lakemask.astype(bool)
        m = m & (~lake)

    return da.where(m)