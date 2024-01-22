""" Game fix for Syberia
"""
#pylint: disable=C0103

import os
import subprocess
from protonfixes import util

def main():
    """ needs player.ini to prevent black screen on load
    """
    if not os.path.isfile('player.ini'):
        subprocess.call(['touch', 'player.ini'])
        f = open('player.ini',"w+")
        f.write("800 600 32 0 BaseCMO.cmo")
        f.close

