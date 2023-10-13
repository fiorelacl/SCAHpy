from setuptools import setup

setup(
    name='SCAHpy',
    version='0.1',
    packages=['scahpy'], # find_packages()
    python_requires='>=3.8',
    install_requires=[
        'numpy',
        'pandas',
        'matplotlib',
        'xarray',
        'wrf-python',
        'metpy',
        'cmocean',
        'cmcrameri',
        'cartopy',
    ]

    author='Fiorela Castillón',
    author_email='fvcastillon@gmail.com',
    url='https://github.com/fiorelacl/SCAHpy',

    description='Paquete para visualizar salidas de \
    modelos numéricos como WRF, CROCO, WRFHydro',

    license='Apache 2.0',
)
