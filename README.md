Processing GPF algorithm provider
==============

QGIS Processing provider for GPF (Graph Processing Framework)-based algorithms. Currently supports selected algorithms from BEAM (http://www.brockmann-consult.de/cms/web/beam/) and NEST (https://earth.esa.int/web/nest/home). In the near future support will be extended to Sentinel Toolboxes (https://sentinel.esa.int/web/sentinel/toolboxes), although limited utilisation of Sentinel-1 (S1) toolbox is already possible by selecting S1 installation directory in place of NEST installation directory in Processing options (see below).

The plugin requires BEAM and/or NEST to be installed for it to be able to access their GPF algorithms. After the installation and activation of the plugin, the providers need to be also activated in the Processing options which are accessible from QGIS main menu (Processing > Options and configuration). You can activate BEAM and NEST providers separately and for each activated provider the path to the software installation needs to be specified:

![](https://github.com/TIGER-NET/screenshots/blob/master/Processing-GPF/activate.png)

After the activation the BEAM and/or NEST algorithms become available in the Processing Toolbox:

![](https://github.com/TIGER-NET/screenshots/blob/master/Processing-GPF/algorithms.png)

The algorithms can be used as any other Processing algorithms, i.e. added to scripts, models, run in batch mode, etc. However, some processing chains (e.g. SAR data pre-processing) require an output of a previous step to be saved in BEAM/NEST format (.DIM) so that it can be used as input for the next step, since not all the metadata is saved in GeoTIFF. Unfortunately .DIM format is not fully supported by GDAL so in those cases the output cannot be properly displayed in QGIS until it is saved as GeoTIFF (when the extra metadata is no longer required) and also those processing chains cannot be build using Processing Toolbox modeller. 

This plugin is part of the Water Observation Information System (WOIS) developed under the TIGER-NET project funded by the European Space Agency as part of the long-term TIGER initiative aiming at promoting the use of Earth Observation (EO) for improved Integrated Water Resources Management (IWRM) in Africa.

Copyright (C) 2014 TIGER-NET (www.tiger-net.org)
