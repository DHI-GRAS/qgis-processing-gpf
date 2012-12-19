from sextante_gpf.SextanteGpfPlugin import SextanteGpfPlugin 
def name():
    return "SEXTANTE BEAM and NEST Provider"
def description():
    return "A plugin that adds BEAM and NEST GPF algorithms to SEXTANTE."
def version():
    return "Version 0.1"
def icon():
    return "/images/beam.png"
def qgisMinimumVersion():
    return "1.0"
def classFactory(iface):
    return SextanteGpfPlugin()