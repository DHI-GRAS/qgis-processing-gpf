Processing GPF algorithm provider
==============

QGIS Processing provider for GPF (Graph Processing Framework)-based algorithms. Currently supports selected algorithms from BEAM (http://www.brockmann-consult.de/cms/web/beam/) and Sentinel-1 Toolbox (S1TBX) (https://sentinel.esa.int/web/sentinel/toolboxes/sentinel-1). In the future support will be extended to other Sentinel Toolboxes (https://sentinel.esa.int/web/sentinel/toolboxes).

The plugin requires BEAM and/or S1TBX to be installed for it to be able to access their GPF algorithms. After the installation and activation of the plugin, the providers need to be also activated in the Processing options which are accessible from QGIS main menu (Processing > Options...). You can activate BEAM and S1TBX providers separately and for each activated provider the path to the software installation needs to be specified:

![](https://github.com/TIGER-NET/screenshots/blob/master/Processing-GPF/activate.png)

After the activation the BEAM and/or S1TBX algorithms become available in the Processing Toolbox:

![](https://github.com/TIGER-NET/screenshots/blob/master/Processing-GPF/algorithms.png)

The algorithms can be used as any other Processing algorithms, i.e. added to scripts, models, run in batch mode, etc. However, some processing chains (e.g. SAR data pre-processing) require an output of a previous step to be saved in BEAM/S1TBX format (.DIM) so that it can be used as input for the next step, since not all the metadata is saved in GeoTIFF. Unfortunately .DIM format is not fully supported by GDAL so in those cases the output cannot be properly displayed in QGIS until it is saved as GeoTIFF (when the extra metadata is no longer required) and also those processing chains cannot be build using Processing Toolbox modeller. 

This plugin is part of the Water Observation Information System (WOIS) developed under the TIGER-NET project funded by the European Space Agency as part of the long-term TIGER initiative aiming at promoting the use of Earth Observation (EO) for improved Integrated Water Resources Management (IWRM) in Africa.

Copyright (C) 2014 TIGER-NET (www.tiger-net.org)
