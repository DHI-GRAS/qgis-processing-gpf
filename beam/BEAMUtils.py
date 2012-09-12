import os
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
    def executeOtb(gpf, progress):
        None