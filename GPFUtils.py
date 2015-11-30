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

import os
import platform
import re
import tempfile
import subprocess
import sys
import logging
from decimal import Decimal 
from processing.tools.system import userFolder, mkdir
from processing.core.ProcessingConfig import ProcessingConfig
from processing.core.ProcessingLog import ProcessingLog
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException

class GPFUtils:
    
    BEAM_FOLDER = "BEAM_FOLDER"
    BEAM_THREADS = "BEAM_THREADS"
    SNAP_FOLDER = "SNAP_FOLDER"
    SNAP_THREADS = "SNAP_THREADS"
    GPF_MODELS_FOLDER = "GPF_MODELS_FOLDER"
    S1TBX_ACTIVATE = "S1TBX_ACTIVATE"
    S2TBX_ACTIVATE = "S2TBX_ACTIVATE"
    
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
    def snapKey():
        return "SNAP"
    
    @staticmethod
    def providerDescription():
        return "SNAP Toolbox (Sentinel Application Platform)"
    
    @staticmethod
    def getKeyFromProviderName(providerName):
        if providerName == "beam":
            return GPFUtils.beamKey()
        elif providerName == "snap":
            return GPFUtils.snapKey()
        else:
            raise GeoAlgorithmExecutionException("Invalid GPF provider name!")
            
    
    @staticmethod
    def programPath(key):
        if key == GPFUtils.beamKey():
            folder = ProcessingConfig.getSetting(GPFUtils.BEAM_FOLDER)
        elif key == GPFUtils.snapKey():
            folder = ProcessingConfig.getSetting(GPFUtils.SNAP_FOLDER)
        else:
            folder = None
            
        if folder == None:
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
        else:
            return ""
    
    @staticmethod
    def modelsFolder():
        folder = ProcessingConfig.getSetting(GPFUtils.GPF_MODELS_FOLDER)
        if folder is None:
            folder = unicode(os.path.join(userFolder(), 'models'))
        folder = unicode(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'gpf_models'))
        mkdir(folder)
        return os.path.abspath(folder)       
    
    @staticmethod
    def executeGpf(key, gpf, progress):
        loglines = []
        if key == GPFUtils.beamKey():
            loglines.append("BEAM execution console output")
        elif key == GPFUtils.s1tbxKey():
            loglines.append("Sentinel-1 Toolbox execution console output")
        else:
            ProcessingLog.addToLog(ProcessingLog.LOG_ERROR, "Unknown GPF algorithm provider")
            return    
        
        # save gpf to temporary file
        gpfFile = open(tempfile.gettempdir() + os.sep + "gpf.xml", 'w')
        gpfFile.write(gpf)
        gpfPath = gpfFile.name
        gpfFile.close()  
        
        
        # execute the gpf
        if key == GPFUtils.beamKey():
            # check if running on windows or other OS
            if platform.system() == "Windows":
                batchFile = "gpt.bat"
            else:
                batchFile = "gpt.sh"
            try:
                threads = int(float(ProcessingConfig.getSetting(GPFUtils.BEAM_THREADS)))
            except:
                threads = 4
            command = ''.join(["\"", GPFUtils.programPath(key), os.sep, "bin", os.sep, batchFile, "\" \"", gpfPath, "\" -e", " -q ",str(threads)])
        elif key == GPFUtils.snapKey():
            # check if running on windows or other OS
            if platform.system() == "Windows":
                batchFile = os.path.join("bin", "gpt.exe")
            else:
                batchFile = os.path.join("bin", "gpt.sh")
            try:
                threads = int(float(ProcessingConfig.getSetting(GPFUtils.S1TBX_THREADS)))
            except:
                threads = 4
            command = ''.join(["\"", GPFUtils.programPath(key), os.sep, batchFile, "\" \"", gpfPath, "\" -e", " -q ",str(threads)])      
        loglines.append(command)
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True).stdout
        line =""
        for char in iter((lambda:proc.read(1)),''):
            line += char
            if "\n" in line:
                loglines.append(line)
                progress.setConsoleInfo(line)
                # force refresh of the execution dialog 
                try:
                    progress.repaint()
                except:
                    pass
                line = ""
            # show progress during S1 Toolbox executions    
            m = re.search("\.(\d{2,3})\%$", line)
            if m:
                progress.setPercentage(int(m.group(1)))
                # force refresh of the execution dialog
                try:
                    progress.repaint()
                except:
                    pass
                
        progress.setPercentage(100)
        ProcessingLog.addToLog(ProcessingLog.LOG_INFO, loglines)
    
    # Get the bands names by calling a java program that uses BEAM functionality 
    @staticmethod
    def getBeamBandNames(filename, programKey, appendProductName = False):
        bands = []
        bandDelim = "__band:"
        if filename == None:
            filename = ""
        else:
            filename = str(filename)    # in case it's a QString
        if programKey == GPFUtils.beamKey():
            command = "\""+os.path.dirname(__file__)+os.sep+"processing_beam_java"+os.sep+"listBeamBands.bat\" "+"\""+GPFUtils.programPath(programKey)+os.sep+"\" "+"\""+filename+"\" "+bandDelim+" "+str(appendProductName)
            proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True).stdout
            for line in iter(proc.readline, ""):
                if bandDelim in line:
                    line = line[len(bandDelim):].strip()
                    #if appendFilename:
                    #    line +="::"+os.path.basename(filename)
                    bands.append(line)
        elif programKey == GPFUtils.snapKey():
            bands = GPFUtils.SNAPProductReaderBand(filename)
        return bands
    
    # Special functionality for S1 Toolbox terrain-correction
    # Get the SAR image pixel sizes by calling a java program that uses S1 Toolbox functionality 
    @staticmethod
    def getS1TbxPixelSize(filename, programKey):
        
        # The value which S1 Toolbox uses to convert resolution from meters to degrees
        # As far as I can see it's independent of the geographical location and is used for
        # both latitude and longitude
        METERSPERDEGREE = Decimal(111319.4907932735600086975208)
        
        pixels = {}
        delim = ":::"
        if filename == None:
            filename = ""
        else:
            filename = str(filename)    # in case it's a QString
        
        command = "\""+os.path.dirname(__file__)+os.sep+"processing_s1tbx_java"+os.sep+"getS1TbxPixelSizes.bat\" "+"\""+GPFUtils.programPath(programKey)+os.sep+"\" "+"\""+filename+"\" "+delim
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True).stdout
        for line in iter(proc.readline, ""):
            ProcessingLog.addToLog(ProcessingLog.LOG_INFO, line)
            if delim in line:
                line = line.strip().split(delim)
                if len(line)>=3:
                    key = line[0]+" ("+line[2]+")"
                    pixels[key] = line[1]
                    if line[2] == "m":
                        key = line[0]+" (deg)"
                        pixels[key] = str(Decimal(line[1])/METERSPERDEGREE)
                    elif line[2] == "deg":
                        key = line[0]+" (m)"
                        pixels[key] = str(Decimal(line[1])*METERSPERDEGREE)
        return pixels
    
    @staticmethod
    def SNAPProductReaderBand(productPath, secondAttempt = False):
        bands = []
        
        if productPath == "":
            return bands
        
        # Temporarily disable logging because otherwise
        # snappy throws an IO error. 
        logging.disable(logging.INFO)
        
        # Import snappy which should be located in the user's home directory
        snappyPath = os.path.join(os.path.expanduser("~"), ".snap", "snap-python")
        if not snappyPath in sys.path:
            sys.path.append(snappyPath)
        try:
            import snappy
            hasSnappy = True
        except:
            hasSnappy = False
            ProcessingLog.addToLog(ProcessingLog.LOG_ERROR, 'Python module snappy is not installed in the user directory. Please run SNAP installer')
            bands = ['Python module snappy is not installed in the user directory', 'Please run SNAP installer']

        if hasSnappy == True:
            try:
                product = snappy.ProductIO.readProduct(productPath)
                for band in product.getBands():
                    bands.append(band.getName())
            except Exception, e:
                # Snappy sometimes throws an error on first try but returns band names 
                # on second try
                if not secondAttempt:
                    bands = GPFUtils.SNAPProductReaderBand(productPath, secondAttempt = True)
                else:
                    bands = ['Snappy exception', 'See Processing log for more details']
                    ProcessingLog.addToLog(ProcessingLog.LOG_ERROR, "Snappy exception: "+str(e))
        
        logging.disable(logging.NOTSET)
        return bands
    
    
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
        
            