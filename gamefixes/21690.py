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
    util.protontricks('wmp11')
    util.protontricks('gfw')

    installpath = os.path.abspath(os.getcwd())
    videopath =  os.path.join(installpath,'nativePC_MT','movie')

    for video in os.listdir(videopath):
        if video.endswith(".wmv") and os.path.getsize(os.path.join(videopath, video)) > 0:
            shutil.move(os.path.join(videopath, video), os.path.join(videopath, video + '.bak'))
            subprocess.call(['touch', os.path.join(videopath, video), os.path.join(videopath)])
