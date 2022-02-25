"""
***************************************************************************
    GPFUtils.py
-------------------------------------
    Copyright (C) 2014 TIGER-NET (www.tiger-net.org)

***************************************************************************
* This plugin is part of the Water Observation Information System (WOIS)  *
* developed under the TIGER-NET project funded by the European Space      *
* Agency as part of the long-term TIGER initiative aiming at promoting    *
* the use of Earth Observation (EO) for improved Integrated Water         *
* Resources Management (IWRM) in Africa.                                  *
*                                                                         *
* WOIS is a free software i.e. you can redistribute it and/or modify      *
* it under the terms of the GNU General Public License as published       *
* by the Free Software Foundation, either version 3 of the License,       *
* or (at your option) any later version.                                  *
*                                                                         *
* WOIS is distributed in the hope that it will be useful, but WITHOUT ANY *
* WARRANTY; without even the implied warranty of MERCHANTABILITY or       *
* FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License   *
* for more details.                                                       *
*                                                                         *
* You should have received a copy of the GNU General Public License along *
* with this program.  If not, see <http://www.gnu.org/licenses/>.         *
***************************************************************************
"""

from builtins import str
from builtins import object
import os
import platform
import re
import tempfile
import subprocess
import sys
import logging
from osgeo import gdal
from decimal import Decimal

from qgis.core import Qgis, QgsMessageLog, QgsProcessingException
from qgis.PyQt.QtCore import QCoreApplication
from processing.tools.system import userFolder, mkdir
from processing.core.ProcessingConfig import ProcessingConfig


class GPFUtils(object):

    BEAM_FOLDER = "BEAM_FOLDER"
    BEAM_THREADS = "BEAM_THREADS"
    SNAP_FOLDER = "SNAP_FOLDER"
    SNAP_THREADS = "SNAP_THREADS"
    GPF_MODELS_FOLDER = "GPF_MODELS_FOLDER"
    S1TBX_ACTIVATE = "S1TBX_ACTIVATE"
    S2TBX_ACTIVATE = "S2TBX_ACTIVATE"
    S3TBX_ACTIVATE = "S3TBX_ACTIVATE"

    @staticmethod
    def beamKey():
        return "BEAM"

    @staticmethod
    def s1tbxKey():
        return "S1Tbx"

    @staticmethod
    def s2tbxKey():
        return "S2Tbx"

    @staticmethod
    def s3tbxKey():
        return "S3Tbx"

    @staticmethod
    def snapKey():
        return "SNAP"

    @staticmethod
    def getKeyFromProviderName(providerName):
        if providerName.lower() == "beam":
            return GPFUtils.beamKey()
        elif providerName.lower() == "snap":
            return GPFUtils.snapKey()
        else:
            raise QgsProcessingException("Invalid GPF provider name!")

    @staticmethod
    def programPath(key):
        if key == GPFUtils.beamKey():
            folder = ProcessingConfig.getSetting(GPFUtils.BEAM_FOLDER)
        elif key == GPFUtils.snapKey():
            folder = ProcessingConfig.getSetting(GPFUtils.SNAP_FOLDER)
        else:
            folder = None

        if folder is None:
            folder = ""
        return folder

    @staticmethod
    def gpfDescriptionPath(key):
        if key == GPFUtils.beamKey():
            return os.path.join(os.path.dirname(__file__), "beam_description")
        elif key == GPFUtils.s1tbxKey():
            return os.path.join(os.path.dirname(__file__), "s1tbx_description")
        elif key == GPFUtils.s2tbxKey():
            return os.path.join(os.path.dirname(__file__), "s2tbx_description")
        elif key == GPFUtils.s3tbxKey():
            return os.path.join(os.path.dirname(__file__), "s3tbx_description")
        elif key == GPFUtils.snapKey():
            return os.path.join(os.path.dirname(__file__), "snap_generic_description")
        else:
            return ""

    @staticmethod
    def gpfDocPath(key):
        if key == GPFUtils.beamKey():
            return os.path.join(os.path.dirname(__file__), "beam_doc")
        elif key == GPFUtils.s1tbxKey():
            return os.path.join(os.path.dirname(__file__), "s1tbx_doc")
        elif key == GPFUtils.s2tbxKey():
            return os.path.join(os.path.dirname(__file__), "s2tbx_doc")
        elif key == GPFUtils.s3tbxKey():
            return os.path.join(os.path.dirname(__file__), "s3tbx_doc")
        elif key == GPFUtils.snapKey():
            return os.path.join(os.path.dirname(__file__), "snap_generic_doc")
        else:
            return ""

    @staticmethod
    def modelsFolder():
        folder = ProcessingConfig.getSetting(GPFUtils.GPF_MODELS_FOLDER)
        if folder is None:
            folder = str(os.path.join(userFolder(), 'models'))
        folder = str(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'gpf_models'))
        mkdir(folder)
        return os.path.abspath(folder)

    @staticmethod
    def executeGpf(key, gpf, progress):
        loglines = []
        if key == GPFUtils.beamKey():
            loglines.append("BEAM execution console output")
        elif key == GPFUtils.snapKey():
            loglines.append("SNAP execution console output")
        else:
            QgsMessageLog.logMessage(GPFUtils.tr("Unknown GPF algorithm provider"),
                                     GPFUtils.tr("Processing"),
                                     Qgis.Critical)
            return

        # save gpf to temporary file
        with open(tempfile.gettempdir() + os.sep + "gpf.xml", 'w') as gpfFile:
            gpfFile.write(gpf)
            gpfPath = gpfFile.name

        # execute the gpf
        if key == GPFUtils.beamKey():
            # check if running on windows or other OS
            if platform.system() == "Windows":
                batchFile = "gpt.bat"
            else:
                batchFile = "gpt.sh"
            try:
                threads = int(float(ProcessingConfig.getSetting(GPFUtils.BEAM_THREADS)))
            except ValueError:
                threads = 4
            command = ''.join(["\"", GPFUtils.programPath(key), os.sep, "bin",
                               os.sep, batchFile, "\" \"", gpfPath, "\" -e", " -q ", str(threads)])
        elif key == GPFUtils.snapKey():
            # check if running on windows or other OS
            batchFile = os.path.join("bin", "gpt")
            try:
                threads = int(float(ProcessingConfig.getSetting(GPFUtils.SNAP_THREADS)))
            except ValueError:
                threads = 4
            command = ''.join(["\"", GPFUtils.programPath(key), os.sep, batchFile,
                               "\" \"", gpfPath, "\" -e", " -q ", str(threads)])
        loglines.append(command)
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                stdin=subprocess.PIPE, stderr=subprocess.STDOUT,
                                universal_newlines=True).stdout
        progress.pushCommandInfo(command)
        line = ""
        for char in iter((lambda: proc.read(1)), ''):
            line += char
            if "\n" in line:
                loglines.append(line)
                if re.search("Error: ", line):
                    progress.reportError(line)
                else:
                    progress.pushConsoleInfo(line)
                line = ""
            # show progress during SNAP executions
            m = re.search("(\d{2,3})\%$", line)
            if m:
                progress.setProgress(int(m.group(1)))
                line = ""

        progress.setProgress(100)
        QgsMessageLog.logMessage("".join(loglines), GPFUtils.tr("Processing"), Qgis.Info)

    # Get the bands names by calling a java program that uses BEAM functionality
    @staticmethod
    def getBeamBandNames(filename, programKey, appendProductName=False):
        bands = []
        bandDelim = "__band:"
        if filename is None:
            filename = ""
        else:
            filename = str(filename)    # in case it's a QString
        if programKey == GPFUtils.beamKey():
            if not os.path.exists(os.path.join(os.path.dirname(__file__), "processing_beam_java",
                                               "listBeamBands.class")):
                bands = ['Missing Java class file', 'See '+os.path.join(os.path.dirname(
                    __file__), "processing_beam_java", "README.txt")+' for more details']
            else:
                command = "\""+os.path.dirname(__file__)+os.sep+"processing_beam_java"+os.sep+\
                          "listBeamBands.bat\" "+"\"" + GPFUtils.programPath(programKey)+os.sep+\
                          "\" "+"\""+filename+"\" "+bandDelim+" "+str(appendProductName)
                proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                        stdin=subprocess.PIPE, stderr=subprocess.STDOUT,
                                        universal_newlines=True).stdout
                for line in iter(proc.readline, ""):
                    if bandDelim in line:
                        line = line[len(bandDelim):].strip()
                        # if appendFilename:
                        #    line +="::"+os.path.basename(filename)
                        bands.append(line)
        elif programKey == GPFUtils.snapKey():
            bands = GPFUtils.getSnapBandNames(filename)
        return bands

    # Import snappy which should be located in the user's home directory
    @staticmethod
    def importSnappy():
        snappyPath = os.path.join(os.path.expanduser("~"), ".snap", "snap-python")
        if snappyPath not in sys.path:
            sys.path.append(snappyPath)

        try:
            # Temporarily disable logging because otherwise
            # snappy throws an IO error.
            logging.disable(logging.INFO)

            import snappy
            from snappy import jpy
            return snappy, jpy
        except Exception:
            QgsMessageLog.logMessage(
                GPFUtils.tr("Python module snappy is not installed in the user directory." +
                            " Please run SNAP installer"),
                GPFUtils.tr("Processing"),
                Qgis.Critical)
            return None, None

    # Use snappy to get a list of band names of a given raster
    @staticmethod
    def getSnapBandNames(productPath, secondAttempt=False):
        bands = []

        productPath, _ = GPFUtils.gdalPathToSnapPath(productPath)

        if productPath == "":
            return bands

        snappy, _ = GPFUtils.importSnappy()
        if snappy is not None:
            try:
                product = snappy.ProductIO.readProduct(productPath)
                bands = product.getBandNames()
                product.closeIO()
                product.dispose()
            except Exception as e:
                # Snappy sometimes throws an error on first try but returns band names
                # on second try
                if not secondAttempt:
                    bands = GPFUtils.getSnapBandNames(productPath, secondAttempt=True)
                else:
                    bands = ['Snappy exception', 'See Processing log for more details']
                    QgsMessageLog.logMessage(GPFUtils.tr("Snappy exception: ")+str(e),
                                             GPFUtils.tr("Processing"),
                                             Qgis.Critical)
        else:
            bands = ['Python module snappy is not installed in the user directory',
                     'Please run SNAP installer']

        logging.disable(logging.NOTSET)
        return bands

    # Use snappy to get a list of polarisations names of a given (S1) raster
    @staticmethod
    def getPolarisations(productPath, secondAttempt=False):
        polarisations = []

        productPath, _ = GPFUtils.gdalPathToSnapPath(productPath)

        if productPath == "":
            return polarisations

        snappy, jpy = GPFUtils.importSnappy()
        if snappy is not None:
            try:
                product = snappy.ProductIO.readProduct(productPath)
                metadata = jpy.get_type(
                    'org.esa.snap.engine_utilities.datamodel.AbstractMetadata').getAbstractedMetadata(product)
                polarisations = \
                    jpy.get_type(
                        'org.esa.s1tbx.insar.gpf.support.Sentinel1Utils').getProductPolarizations(metadata)
                product.closeIO()
                product.dispose()
            except Exception as e:
                # Snappy sometimes throws an error on first try but returns band names
                # on second try
                if not secondAttempt:
                    polarisations = GPFUtils.getPolarisations(productPath, secondAttempt=True)
                else:
                    polarisations = ['Snappy exception', 'See Processing log for more details']
                    QgsMessageLog.logMessage(GPFUtils.tr("Snappy exception: ")+str(e),
                                             GPFUtils.tr("Processing"),
                                             Qgis.Critical)
        else:
            polarisations = ['Python module snappy is not installed in the user directory',
                             'Please run SNAP installer']

        logging.disable(logging.NOTSET)
        return polarisations

    @staticmethod
    def indentXML(elem, level=0):
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                GPFUtils.indentXML(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    # GDAL has ability to open S1 and S2 data since version 2.1. However, GDAL sometimes
    # prepends or postpends text to the file path (especially in case of S2 images with
    # sub-datasets). Those discrepancies have to be resolved before the path can be used in
    # a SNAP GPF graph.
    @staticmethod
    def gdalPathToSnapPath(gdalPath):
        snapPath = gdalPath
        dataFormat = ""
        # Sentinel-2 data
        # The path to S2 XML file and data format has to be extracted from GDAL path string.
        match = re.match(
            "SENTINEL2_L[123][ABC](_TILE)?:(/vsizip/)?(.[:]?[^:]+):([^:]*):?(.*)", gdalPath)
        if match:
            path = match.group(3)
            proj = match.group(5)
            if not proj:
                f = gdal.Open(gdalPath, gdal.GA_ReadOnly)
                proj = f.GetProjection()
                proj = "EPSG_" + \
                    re.search('AUTHORITY\[\"EPSG\",\"([0-9]{5})\"\]\]$', proj).group(1)
                f = None
            snapPath = path
            hemisphere = "N" if proj[7] == '6' else "S"
            dataFormat = "SENTINEL-2-MSI-MultiRes-UTM"+proj[8:10]+hemisphere
        return snapPath, dataFormat

    @staticmethod
    def tr(string, context=''):
        if context == '':
            context = 'Grass7Utils'
        return QCoreApplication.translate(context, string)
