""" Ceville
Works with dotnet35sp1 only, now without needing Proton5
Videos still don't work. 
"""
#pylint: disable=C0103

import os
import subprocess
from protonfixes import util

def main():
    util.protontricks('dotnet35sp1')
    #Videos play and audio works but screen is black.
    #util.protontricks('quartz')
    #util.protontricks('klite')
    if os.path.isdir('./data/shared/videos'):
        subprocess.call(['mv', './data/shared/videos', './data/shared/_videos'])
    util.winedll_override('libvkd3d-1', 'n')
