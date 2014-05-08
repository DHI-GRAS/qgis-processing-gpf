import os
import re
import tempfile
import subprocess
from decimal import Decimal 
from processing.core.ProcessingConfig import ProcessingConfig
from processing.core.ProcessingLog import ProcessingLog

class GPFUtils:
    
    BEAM_FOLDER = "BEAM_FOLDER"
    BEAM_THREADS = "BEAM_THREADS"
    NEST_FOLDER = "NEST_FOLDER"
    NEST_THREADS = "NEST_THREADS"
    
    @staticmethod
    def beamKey():
        return "BEAM"
    
    @staticmethod
    def nestKey():
        return "NEST"
    
    @staticmethod
    def programPath(key):
        if key == GPFUtils.beamKey():
            folder = ProcessingConfig.getSetting(GPFUtils.BEAM_FOLDER)
        elif key == GPFUtils.nestKey():
            folder = ProcessingConfig.getSetting(GPFUtils.NEST_FOLDER)
        else:
            folder = None
            
        if folder == None:
            folder = ""
        return folder
    
    @staticmethod
    def gpfDescriptionPath(key):
        if key == GPFUtils.beamKey():
            return os.path.join(os.path.dirname(__file__), "beam_description")
        elif key == GPFUtils.nestKey():
            return os.path.join(os.path.dirname(__file__), "nest_description")
        else:
            return ""
    
    @staticmethod
    def gpfDocPath(key):
        if key == GPFUtils.beamKey():
            return os.path.join(os.path.dirname(__file__), "beam_doc") 
        elif key == GPFUtils.nestKey():
            return os.path.join(os.path.dirname(__file__), "nest_doc") 
        else:
            return ""
           
    
    @staticmethod
    def executeGpf(key, gpf, output, sourceFiles, progress):
        loglines = []
        if key == GPFUtils.beamKey():
            loglines.append("BEAM execution console output")
        elif key == GPFUtils.nestKey():
            loglines.append("NEST execution console output")
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
            try:
                threads = int(float(ProcessingConfig.getSetting(GPFUtils.BEAM_THREADS)))
            except:
                threads = 4
            command = ''.join(["\"", GPFUtils.programPath(key), os.sep, "bin", os.sep, "gpt.bat\" \"", gpfPath, "\" -e", " -q ",str(threads), " -t \"", output, "\" ", sourceFiles])
            #command = ''.join(["\"", GPFUtils.programPath(key), os.sep, "bin", os.sep, "gpt.bat\" \"", gpfPath, "\" -e ", sourceFiles])
        elif key == GPFUtils.nestKey():
            try:
                threads = int(float(ProcessingConfig.getSetting(GPFUtils.NEST_THREADS)))
            except:
                threads = 4
            command = ''.join(["\"", GPFUtils.programPath(key), os.sep, "gpt.bat\" \"", gpfPath, "\" -e", " -q ",str(threads), " -t \"", output, "\" ", sourceFiles])   
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
            # show progress during NEST executions    
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
    
    # Special functionality for NEST terrain-correction
    # Get the SAR image pixel sizes by calling a java program that uses NEST functionality 
    @staticmethod
    def getNESTPixelSize(filename, programKey):
        
        # The value which NEST uses to convert resolution from meters to degrees
        # As far as I can see it's independent of the geographical location and is used for
        # both latitude and longitude
        METERSPERDEGREE = Decimal(111319.4907932735600086975208)
        
        pixels = {}
        delim = ":::"
        if filename == None:
            filename = ""
        else:
            filename = str(filename)    # in case it's a QString
        
        command = "\""+os.path.dirname(__file__)+os.sep+"processing_nest_java"+os.sep+"getNESTPixelSizes.bat\" "+"\""+GPFUtils.programPath(programKey)+os.sep+"\" "+"\""+filename+"\" "+delim
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
            