""" Game fix for Syberia
"""
#pylint: disable=C0103

import os
import subprocess

def main():
    """ needs player.ini to prevent black screen on load
    """
    if not os.path.isfile('player.ini'):
        subprocess.call(['touch', 'player.ini'])
        with open('player.ini',"w+", encoding='utf-8') as f:
            f.write("800 600 32 0 BaseCMO.cmo")
