from setuptools import setup

setup(
    name='SCAHpy',
    version='0.0.1',
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
        'geopandas'
    ]

    author='Fiorela Castillón',
    author_email='fvcastillon@gmail.com',
    url='https://github.com/fiorelacl/SCAHpy',

    description='Package to process and analyze outputs from \
    atmospheric, oceanic and Hydrological components from IGP-RESM-COW model',

    license='MIT License',
)
