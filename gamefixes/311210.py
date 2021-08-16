""" Game workaround for Call of Duty Black Ops III
"""
#pylint: disable=C0103

import os
import subprocess
from protonfixes import util

def main():
    """ Graphics API workaround
    """
    if os.path.exists('video'):
        if os.path.exists('video-backup'):
            subprocess.call(['rm', '-Rf', 'video-backup'])
        subprocess.call(['mv', 'video', 'video-backup'])

