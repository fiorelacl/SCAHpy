<div style="text-align: center;">
<img width="500" src="https://github.com/fiorelacl/SCAHpy/blob/main/docs/cover.png?raw=true" >
</div>

## **What is SCAHpy?**

**SCAHpy** (System for Coupled Atmosphere–Hydrosphere Analysis in Python) is an open-source scientific Python package that facilitates the analysis and visualization of outputs from the atmospheric, oceanic, and hydrological components of the Geophysical Institute of Peru Regional Earth System Model — **IGP-RESM-COW**.

It provides tools for processing, diagnosing, and visualizing model results in a modular and reproducible way, enabling seamless workflows for multi-component climate simulations.

<div style="text-align: center;">
<img width="450" src="https://github.com/fiorelacl/SCAHpy/blob/main/docs/cow_model.jpg?raw=true" >
</div>

## **Why SCAHpy?**

The atmospheric and oceanic components of coupled models generate **large volumes of output data**, making post-processing and diagnostics complex.  
**SCAHpy** simplifies these tasks by streamlining data handling, coordinate management, and temporal adjustments (e.g., conversion to local time), while integrating high-level plotting utilities for maps, sections, and time-series analyses.

Its design is inspired by the principles of **open and reproducible science**, promoting accessibility and collaboration across research institutions.

## **How to use SCAHpy?**

SCAHpy can be used as a standalone Python package or within high-performance computing environments such as the **HPC-IGP Cluster**, which hosts more than 22 years of regional coupled simulations over the Peruvian domain.


<div class="note" style='background-color:#e4f2f7; color: #1f2426; border-left: solid #add8e6 5px; border-radius: 2px; padding:0.3em;'>
<span>
<p style='margin-top:0.4em; text-align:left; margin-right:0.5em'>
<b>Note:</b> <i>SCAHpy has been developed and validated using IGP-RESM-COW model outputs. However, it is fully compatible with any WRF or CROCO based dataset or NetCDF output following CF-Conventions. We welcome community contributions and extensions!</i> </p>
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

