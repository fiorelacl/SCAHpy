<div style="text-align: center;">
<img width="500" src="https://github.com/fiorelacl/SCAHpy/blob/main/docs/cover.png?raw=true" >
</div>

## **What is SCAHpy?**

***SCAHpy*** is an open-source Python package that facilitate the analysis and visualization of the ouputs from atmospheric, oceaninc and hydrological component from the Geophysical Institute of Peru Regional Earth System Model Croco-Oasis-WRF (IGP-RESM-COW)

<div style="text-align: center;">
<img width="450" src="https://github.com/fiorelacl/SCAHpy/blob/main/docs/cow_model.jpg?raw=true" >
</div>

## **Why is SCAHpy?**

Atmospheric component of the coupled model generate a large volumes of output data, making the analysis of model data harder. SCAHpy facilitates the manage of this volumes of data, also enables a manage of coordinates and times to local times. 

## **How to use SCAHpy?**

SCAHpy can be used as a standalone package or it can also be run on the HPC-IGP-Cluster, which has the diagnostic simulations of 22 years of runnings centered on Peru Region. 


<div class="note" style='background-color:#e4f2f7; color: #1f2426; border-left: solid #add8e6 5px; border-radius: 2px; padding:0.3em;'>
<span>
<p style='margin-top:0.4em; text-align:left; margin-right:0.5em'>
<b>Note:</b> <i>SCAHpy has been developed and tested using IGP-RESM-COW model outputs. However, it is designed to work with any WRF outputs. We are open to contributions from users!</i> </p>
</span>
</div>


# Documentation

The official documentation is hosted here: [Documentation](https://fiorelacl.github.io/SCAHpy/)

## Installation

#### Using Mamba

1. First, download and install mamba or miniconda through [Miniforge](https://github.com/conda-forge/miniforge) .

2. The easiest way to install SCAHpy and the above mentioned dependencies is to use the environment.yml from the [repository](https://github.com/fiorelacl/SCAHpy/). Open a terminal, then run the following command:

```bash
 mamba env create --file environment.yml -n scahpy_env
```

#### Using pip

1. To install SCAHpy directly. Open a terminal, then run the following command:

```bash
 pip install scahpy
```

<div class="note" style='background-color:#e4f2f7; color: #1f2426; border-left: solid #add8e6 5px; border-radius: 2px; padding:0.3em;'>
<span>
<p style='margin-top:0.4em; text-align:left; margin-right:0.5em'>
<b>Note:</b> <i> Checkout the contribution page if you want to get involved and help maintain or develop SCAHpy </i> </p>
</span>
</div>

