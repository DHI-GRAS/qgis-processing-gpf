import os
import tempfile
import subprocess
from sextante.core.SextanteConfig import SextanteConfig
from sextante.core.SextanteLog import SextanteLog
from sextante.core.SextanteUtils import SextanteUtils

class BEAMUtils:
    
    BEAM_FOLDER = "BEAM_FOLDER"
    
    @staticmethod
    def beamPath():
        folder = SextanteConfig.getSetting(BEAMUtils.BEAM_FOLDER)
        if folder == None:
            folder = ""
        return folder
    
    @staticmethod
    def beamDescriptionPath():
        return os.path.join(os.path.dirname(__file__), "description")
    
    @staticmethod
    def beamDocPath():
        return os.path.join(os.path.dirname(__file__), "doc")    
    
    @staticmethod
    def executeBeam(gpf, output, sourceFiles, progress):
        loglines = []
        loglines.append("BEAM execution console output")
        
        # save gpf to temporary file
        gpfFile = open(tempfile.gettempdir() + os.sep + "beamGPF.tmp", 'w')
        gpfFile.write(gpf)
        gpfPath = gpfFile.name
        gpfFile.close()  
        
        # execute the gpf
        command = ''.join(["\"", BEAMUtils.beamPath(), os.sep, "bin", os.sep, "gpt.bat\" \"", gpfPath, "\" -e", " -t \"", output, "\" ", sourceFiles])
        loglines.append(command)
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True).stdout
        for line in iter(proc.readline, ""):
            loglines.append(line)
            
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
        
        command = "\""+os.path.dirname(__file__)+os.sep+"sextante_beam_java"+os.sep+"listBeamBands.bat\" "+"\""+BEAMUtils.beamPath()+os.sep+"\" "+"\""+filename+"\" "+bandDelim
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True).stdout
        for line in iter(proc.readline, ""):
            if bandDelim in line:
                bands.append(line[len(bandDelim):])
                
        return bands
         
            