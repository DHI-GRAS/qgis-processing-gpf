import os
import re
import tempfile
import subprocess
from sextante.core.SextanteConfig import SextanteConfig
from sextante.core.SextanteLog import SextanteLog

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
            try:
                threads = int(float(SextanteConfig.getSetting(GPFUtils.BEAM_THREADS)))
            except:
                threads = 4
            command = ''.join(["\"", GPFUtils.programPath(key), os.sep, "bin", os.sep, "gpt.bat\" \"", gpfPath, "\" -e", " -q ",str(threads), " -t \"", output, "\" ", sourceFiles])
            #command = ''.join(["\"", GPFUtils.programPath(key), os.sep, "bin", os.sep, "gpt.bat\" \"", gpfPath, "\" -e ", sourceFiles])
        elif key == GPFUtils.nestKey():
            try:
                threads = int(float(SextanteConfig.getSetting(GPFUtils.NEST_THREADS)))
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
                line = ""
            # show progress during NEST executions    
            m = re.search("\.(\d{2,3})\%$", line)
            if m:
                progress.setPercentage(int(m.group(1)))
                
        progress.setPercentage(100)
        SextanteLog.addToLog(SextanteLog.LOG_INFO, loglines)
    
    # Get the bands names by calling a java program that uses BEAM functionality 
    @staticmethod
    def getBeamBandNames(filename, programKey, appendProductName = False):
        bands = []
        bandDelim = "__band:"
        if filename == None:
            filename = ""
        else:
            filename = str(filename)    # in case it's a QString
        
        command = "\""+os.path.dirname(__file__)+os.sep+"sextante_beam_java"+os.sep+"listBeamBands.bat\" "+"\""+GPFUtils.programPath(programKey)+os.sep+"\" "+"\""+filename+"\" "+bandDelim+" "+str(appendProductName)
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True).stdout
        for line in iter(proc.readline, ""):
            if bandDelim in line:
                line = line[len(bandDelim):].strip()
                #if appendFilename:
                #    line +="::"+os.path.basename(filename)
                bands.append(line)
                
        return bands
         
            