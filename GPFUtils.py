import os
import tempfile
import subprocess
from sextante.core.SextanteConfig import SextanteConfig
from sextante.core.SextanteLog import SextanteLog
from sextante.core.SextanteUtils import SextanteUtils

class GPFUtils:
    
    BEAM_FOLDER = "BEAM_FOLDER"
    NEST_FOLDER = "NEST_FOLDER"
    
    @staticmethod
    def beamKey():
        return "BEAM"
    
    @staticmethod
    def nestKey():
        return "NEST"
    
    @staticmethod
    def programPath(key):
        if key == GPFUtils.beamKey():
            folder = SextanteConfig.getSetting(GPFUtils.BEAM_FOLDER)
        elif key == GPFUtils.nestKey():
            folder = SextanteConfig.getSetting(GPFUtils.NEST_FOLDER)
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
            SextanteLog.addToLog(SextanteLog.LOG_ERROR, "Unknown GPF algorithm provider")
            return    
        
        # save gpf to temporary file
        gpfFile = open(tempfile.gettempdir() + os.sep + "gpf.xml", 'w')
        gpfFile.write(gpf)
        gpfPath = gpfFile.name
        gpfFile.close()  
        
        # execute the gpf
        if key == GPFUtils.beamKey():
            command = ''.join(["\"", GPFUtils.programPath(key), os.sep, "bin", os.sep, "gpt.bat\" \"", gpfPath, "\" -e", " -t \"", output, "\" ", sourceFiles])
        elif key == GPFUtils.nestKey():
            command = ''.join(["\"", GPFUtils.programPath(key), os.sep, "gpt.bat\" \"", gpfPath, "\" -e", " -t \"", output, "\" ", sourceFiles])     
        loglines.append(command)
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True).stdout
        for line in iter(proc.readline, ""):
            loglines.append(line)
            progress.setConsoleInfo(line)
            
        progress.setPercentage(100)
        SextanteLog.addToLog(SextanteLog.LOG_INFO, loglines)
    
    # Get the bands names by calling a java program that uses BEAM functionality 
    @staticmethod
    def getBeamBandNames(filename):
        bands = []
        bandDelim = "__band:"
        if filename == None:
            filename = ""
        else:
            filename = str(filename)    # in case it's a QString
        
        command = "\""+os.path.dirname(__file__)+os.sep+"sextante_beam_java"+os.sep+"listBeamBands.bat\" "+"\""+GPFUtils.programPath(GPFUtils.beamKey())+os.sep+"\" "+"\""+filename+"\" "+bandDelim
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True).stdout
        for line in iter(proc.readline, ""):
            if bandDelim in line:
                bands.append(line[len(bandDelim):])
                
        return bands
         
            