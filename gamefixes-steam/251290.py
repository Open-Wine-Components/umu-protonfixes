""" Game fix for The Legend of Heroes: Trails in the Sky SC
"""
# pylint: disable=C0103

from protonfixes import util

def main():
    util.protontricks('quartz') # Cutscene fixes
    util.protontricks('amstream')
    util.protontricks('lavfilters')
    util.winedll_override('dinput8', 'n,b') # Set for the SoraVoice mod
