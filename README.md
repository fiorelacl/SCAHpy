<div style="text-align: center;">
<img width="500" src="https://github.com/fiorelacl/SCAHpy/blob/main/docs/assets/cover.png?raw=true" >
</div>

<div style="
  background-color:#f1f6ff;
  border-left: 6px solid #4d79ff;
  padding: 0.9em 1.1em;
  margin: 1.4em 0;
  border-radius: 6px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
">
  <h3 style="margin-top:0; margin-bottom:0.4em;">📢 SCAHpy v2.0 — Major Release</h3>
  <p style="margin:0;">
    Version <b>2.0</b> of SCAHpy is now available with improved stability,
    new analytical and plotting features, and a fully reorganized documentation framework.<br><br>
    The official documentation is now provided in <b>two languages</b>: <b>English</b> and <b>Spanish</b>,
    increasing accessibility for both regional and international research communities.
  </p>
</div>

<p align="center">

  <!-- PyPI version -->
  <a href="https://pypi.org/project/scahpy/">
    <img src="https://img.shields.io/pypi/v/scahpy?color=4d79ff&label=PyPI%20Version&logo=pypi" alt="PyPI version">
  </a>

  <!-- Python versions -->
  <a href="https://pypi.org/project/scahpy/">
    <img src="https://img.shields.io/pypi/pyversions/scahpy.svg?color=4d79ff&label=Python&logo=python" alt="Python versions">
  </a>

  <!-- Documentation -->
  <a href="https://fiorelacl.github.io/SCAHpy/">
    <img src="https://img.shields.io/badge/Docs-English%20%7C%20Español-4d79ff?logo=readthedocs&logoColor=white" alt="Documentation">
  </a>

  <!-- License -->
<a href="https://github.com/fiorelacl/SCAHpy/blob/main/LICENSE">
  <img src="https://img.shields.io/github/license/fiorelacl/SCAHpy?color=4d79ff&label=License" alt="License">
</a>

</p>


## **What is SCAHpy?**

**SCAHpy** (System for Coupled Atmosphere–Hydrosphere Analysis in Python) is an open-source scientific Python package that facilitates the analysis and visualization of outputs from the atmospheric, oceanic, and hydrological components of the Geophysical Institute of Peru Regional Earth System Model — **IGP-RESM-COW**.

It provides tools for processing, diagnosing, and visualizing model results in a modular and reproducible way, enabling seamless workflows for multi-component climate simulations.

<div style="text-align: center;">
<img width="450" src="https://github.com/fiorelacl/SCAHpy/blob/main/docs/assets/cow_model.jpg?raw=true" >
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
<b>Note:</b> <i>SCAHpy has been developed and validated using IGP-RESM-COW model outputs. However, it is fully compatible with any WRF or CROCO-based dataset or NetCDF output following CF-Conventions. Community contributions are welcome!</i>
</p>
</span>
</div>

# Documentation

The official documentation is hosted here:  
👉 https://fiorelacl.github.io/SCAHpy/

It is available in **English** and **Spanish**, with a complete bilingual structure using Quarto profiles.

## Installation

### Using Mamba

1. Install mamba or miniconda through [Miniforge](https://github.com/conda-forge/miniforge).
2. Create the environment using the included `environment.yml`:

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

