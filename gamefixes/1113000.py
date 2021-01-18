""" Game fix for Persona 4 Golden
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ installs devenum, quartz, wmp9 and adjust pulse latency
    """

    # Fix pre-rendered cutscene playback
    util.protontricks('wmp9')
    util.protontricks('quartz')
    util.protontricks('qcap')
    util.protontricks('qasf')
    util.protontricks('d3dx11_43')
    util.protontricks('d3dcompiler_43')
    util.protontricks('klite')
    util.set_environment('WINEDLLOVERRIDES','mfplay=n')

