from sextante_beam.SextanteBeamPlugin import SextanteBeamPlugin 
def name():
    return "SEXTANTE BEAM Provider"
def description():
    return "A plugin that adds BEAM GPT algorithms to SEXTANTE."
def version():
    return "Version 0.1"
def icon():
    return "/images/beam.png"
def qgisMinimumVersion():
    return "1.0"
def classFactory(iface):
    return SextanteBeamPlugin()