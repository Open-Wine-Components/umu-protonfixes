""" Game fix for Pentiment
"""
#pylint: disable=C0103
import os
import subprocess
from protonfixes import util

def main():
    """ Remove SpeechSynthesisWrapper.dll causing the game to crash on startup
    """

    if os.path.exists('Pentiment_Data/Plugins/x86_64/SpeechSynthesisWrapper.dll'):
        subprocess.call(['rm', '-rf', 'Pentiment_Data/Plugins/x86_64/SpeechSynthesisWrapper.dll'])
