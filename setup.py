from setuptools import setup

setup(
    # Needed to silence warnings (and to be a worthwhile package)
    name='SCAHpy',
    url='https://github.com/fiorelacl/SCAHpy',
    author='Fiorela Castillón',
    author_email='fcastillon@igp.gob.pe',
    # Needed to actually package something
    packages=['scahpy'],
    python_requires='>=3.8',
    # *strongly* suggested for sharing
    version='0.1',
    # The license can be anything you like
    license='Apache 2.0',
    description='Paquete para visualizar salidas de modelos numéricos como WRF-WRFHydro',
    # We will also need a readme eventually (there will be a warning)
    # long_description=open('README.txt').read(),
)
