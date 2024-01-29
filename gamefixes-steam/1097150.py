""" Game fix for Fall Guys
"""
#pylint: disable=C0103
import os
import glob
import subprocess
from protonfixes import util

def main():
    """ Create symlink of eac so at the right location
    """
    util.install_eac_runtime()
    util.set_environment('DOTNET_BUNDLE_EXTRACT_BASE_DIR', '')
