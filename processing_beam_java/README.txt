listBeamBands.class might be missing from this directory due to QGIS policy of not distributing plugins which include compiled files.

If that is the case you can download the missing file from https://github.com/DHI-GRAS/processing_gpf/blob/GW-A_dev/processing_beam_java/listBeamBands.class or compile it yourself from listBeamBands.java. 

In the latter case, all the jar's in BEAM_FOLDER/lib and BEAM_FOLDER/modules should be on the build path together with BEAM JRE.

The compilation has to be into JRE 1.7 (or lower) as this is the version used by BEAM at the moment.