""" Game fix for Persona 4 Golden
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ installs devenum, quartz, wmp9 and adjust pulse latency
    """

    # Fix pre-rendered cutscene playback
    util.protontricks('vcrun2019_ge')
    util.protontricks('d3dcompiler_47')

