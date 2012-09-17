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
    def executeBeam(gpf, output, progress):
        loglines = []
        loglines.append("BEAM execution console output")
        
        # save gpf to temporary file
        gpfFile = open(tempfile.gettempdir() + os.sep + "beamGPF.tmp", 'w')
        gpfFile.write(gpf)
        gpfPath = gpfFile.name
        gpfFile.close()  
        
        # execute the gpf
        command = ''.join(["\"", BEAMUtils.beamPath(), os.sep, "gpt.bat\" \"", gpfPath, "\" -e", " -t \"", output, "\""])
        loglines.append(command)
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True).stdout
        for line in iter(proc.readline, ""):
            loglines.append(line)
            
           
        progress.setPercentage(100)
        SextanteLog.addToLog(SextanteLog.LOG_INFO, loglines)