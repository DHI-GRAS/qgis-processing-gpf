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
from decimal import Decimal 
from processing.core.ProcessingConfig import ProcessingConfig
from processing.core.ProcessingLog import ProcessingLog

class GPFUtils:
    
    BEAM_FOLDER = "BEAM_FOLDER"
    BEAM_THREADS = "BEAM_THREADS"
    S1TBX_FOLDER = "S1TBX_FOLDER"
    S1TBX_THREADS = "S1TBX_THREADS"
    
    @staticmethod
    def beamKey():
        return "BEAM"
    
    @staticmethod
    def s1tbxKey():
        return "S1Tbx"
    
    @staticmethod
    def programPath(key):
        if key == GPFUtils.beamKey():
            folder = ProcessingConfig.getSetting(GPFUtils.BEAM_FOLDER)
        elif key == GPFUtils.s1tbxKey():
            folder = ProcessingConfig.getSetting(GPFUtils.S1TBX_FOLDER)
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
        else:
            return ""
    
    @staticmethod
    def gpfDocPath(key):
        if key == GPFUtils.beamKey():
            return os.path.join(os.path.dirname(__file__), "beam_doc") 
        elif key == GPFUtils.s1tbxKey():
            return os.path.join(os.path.dirname(__file__), "s1tbx_doc") 
        else:
            return ""
           
    
    @staticmethod
    def executeGpf(key, gpf, output, sourceFiles, progress):
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
        
        # check if running on windows or other OS
        if platform.system() == "Windows":
            batchFile = "gpt.bat"
        else:
            batchFile = "gpt.sh"
        
        # execute the gpf
        if key == GPFUtils.beamKey():
            try:
                threads = int(float(ProcessingConfig.getSetting(GPFUtils.BEAM_THREADS)))
            except:
                threads = 4
            command = ''.join(["\"", GPFUtils.programPath(key), os.sep, "bin", os.sep, batchFile, "\" \"", gpfPath, "\" -e", " -q ",str(threads), " -t \"", output, "\" ", sourceFiles])
            #command = ''.join(["\"", GPFUtils.programPath(key), os.sep, "bin", os.sep, "gpt.bat\" \"", gpfPath, "\" -e ", sourceFiles])
        elif key == GPFUtils.s1tbxKey():
            try:
                threads = int(float(ProcessingConfig.getSetting(GPFUtils.S1TBX_THREADS)))
            except:
                threads = 4
            command = ''.join(["\"", GPFUtils.programPath(key), os.sep, batchFile, "\" \"", gpfPath, "\" -e", " -q ",str(threads), " -t \"", output, "\" ", sourceFiles])   
            #command = ''.join(["\"", GPFUtils.programPath(key), os.sep, "gpt.bat\" \"", gpfPath, "\" -e ", "-q 8 ", sourceFiles])    
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
        
        command = "\""+os.path.dirname(__file__)+os.sep+"processing_beam_java"+os.sep+"listBeamBands.bat\" "+"\""+GPFUtils.programPath(programKey)+os.sep+"\" "+"\""+filename+"\" "+bandDelim+" "+str(appendProductName)
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True).stdout
        for line in iter(proc.readline, ""):
            if bandDelim in line:
                line = line[len(bandDelim):].strip()
                #if appendFilename:
                #    line +="::"+os.path.basename(filename)
                bands.append(line)
                
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
            