""" Game fix for Resident Evil 5
"""
#pylint: disable=C0103

import os
import shutil
import subprocess
from protonfixes import util

def main():
    """ Installs wmp11
    """
    util.protontricks('gfw')
    util.protontricks('wmp11')

