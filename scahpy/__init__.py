__all__ = [
    'in_out',
    'met_diag',
    'spatial_scales',
    'temp_scales',
]

from importlib import resources
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

# Version of the realpython-reader package
__version__ = "0.0.1"
