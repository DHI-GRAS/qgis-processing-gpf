Processing GPF algorithm provider
==============

QGIS Processing provider for GPF (Graph Processing Framework)-based algorithms. Currently supports selected algorithms from BEAM 5.0 (http://www.brockmann-consult.de/cms/web/beam/) and Sentinel Application Platform 5.0 (SNAP - http://step.esa.int).

The plugin requires BEAM and/or SNAP to be installed for it to be able to access their GPF algorithms. If SNAP algorithms are to be used then snappy (SNAP Python interface) should be installed together with SNAP. After the installation and activation of the plugin, the providers need to be also activated in the Processing options which are accessible from QGIS main menu (Processing > Options...). You can activate BEAM and SNAP providers separately and for SNAP you can also choose to activate algorithms from individual Sentinel Toolboxes. For each activated provider the path to the software installation needs to be specified.

![](https://github.com/TIGER-NET/screenshots/blob/master/Processing-GPF/activate.png)

After the activation the BEAM and/or SNAP algorithms become available in the Processing Toolbox. The SNAP algorithms are organised in a structure mimicking the location of each algorithm in the SNAP Desktop main menu. Additionally, the icon of each SNAP algorithm indicates which Sentinel Toolbox it came from.

![](https://github.com/TIGER-NET/screenshots/blob/master/Processing-GPF/algorithms.png)

The algorithms can be used as any other Processing algorithms, i.e. added to scripts, models, run in batch mode, etc. However, some processing chains might require an output of a previous step to be saved in BEAM/SNAP format (.DIM) so that it can be used as input for the next step, since not all the metadata might be saved in GeoTIFF. Unfortunately .DIM format is not fully supported by GDAL so in those cases the output cannot be properly displayed in QGIS until it is saved as GeoTIFF (when the extra metadata is no longer required) and also those processing chains cannot be build using Processing Toolbox modeller. 

To overcome this issue, and to improve the performance of SNAP-based processing chains, it is now possible to build models using only SNAP algorithms using the GPF Graph Builder functionality. The models are saved in an XML format compatible with the SNAP Desktop (GPF) format. Therefore, it should be possible to open and run any SNAP graph made in QGIS in SNAP Desktop. Similarly, it should be possible to open graphs made in SNAP Desktop in QGIS, as long as the required algorithms are available in the QGIS Processing Toolbox through this plugin.

![](https://github.com/TIGER-NET/screenshots/blob/master/Processing-GPF/graphs.png)

This plugin is part of the Water Observation Information System (WOIS) developed under the TIGER-NET project funded by the European Space Agency as part of the long-term TIGER initiative aiming at promoting the use of Earth Observation (EO) for improved Integrated Water Resources Management (IWRM) in Africa.

Copyright (C) 2014 TIGER-NET (www.tiger-net.org)
