# ALAN

This repository contains code for calculating the Artificial Light at Night (ALAN) Under the Sea atlas.

To run the code you can set up a conda environment (recommend using mamba), with required dependencies:
```
   conda env create -f environment.yml
   conda activate ALAN_env
```

For generating the critical depth output for the identified regions, for all months, there is a script: `GetAlanTiles.py`. To run for all regions and months, just provide 'output_dir' as an argument. Specific region(s) or month(s) can be chosen with the `--regions` and `--months` arguments. This script relies on the `alan_tools.alan_tile` module.

Available regions of interest:
   * EuropeMed
   * MidE_NInd
   * NInd_FarE
   * FarE_Isl
   * Oceania
   * PacRim
   * NAm
   * CAm
   * SAm
   * NAfr
   * SAfr

Months in the form MM from 01-12

Example execution line:
```
GetAlanTiles.py /path/to/output --regions Oceania PacRim --months 03 10
```

Before running this script you should update the settings in the following files:
 * ``alan_tools/config.py`` - In particular checking that the input file paths point to data that is available on your system (you can alternatively override these settings with arguments passed to script).
 * ``alan_tools/file_attributes.py`` - This file contains the meta data to be stored in the output files. Update the attributes as needed, paying particulary attention to the publication date and contact details attributes. You can add/remove attribute, noting that the placeholders (`XXXX_PLACEHOLDER`) need to be kept in place for the code to run successfully. 

You may override the input file paths by providing them as arguments to the GetAlanTiles script, e.g.
```
   GetAlanTiles.py /path/to/output \
       --kd_dir  /path/to/kd_data_dir \
       --kd_fpattern  'ESACCI-OC-MAPPED-CLIMATOLOGY-1M_MONTHLY_4km_GEO_PML_OCx_QAA-Kd-{month}-fv4.0.nc' \
       --falchi_path  /path/to/falchi_data_dir/World_Atlas_2015.tif \
       --landmask_path  /path/to/landmask_data_dir/landmask30as.zarr/
```

Note that the code assumes specific formats for the input files:
 * Kd data expected in NetCDF format,
 * The Falchi data expected in GeoTIFF format,
 * The landmask expected in Zarr file storage format.



[![CC BY-NC 4.0][cc-by-nc-image]][cc-by-nc]<br />This work is licensed under a [Creative Commons Attribution-NonCommercial 4.0 International License][cc-by-nc].

[cc-by-nc]: http://creativecommons.org/licenses/by-nc/4.0/
[cc-by-nc-image]: https://i.creativecommons.org/l/by-nc/4.0/88x31.png
