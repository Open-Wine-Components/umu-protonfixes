""" Cease to Breathe
Replace included nwjs(0.71) wich doesn't work with 0.86
Fix cursor hitbox (set frame=false in package.json)
Updated from 0.85 that didn't display custom cursors.
"""
#pylint: disable=C0103

import os
import glob
import shutil
import urllib.request
import zipfile
import subprocess
from protonfixes import util

def main():
    util.replace_command('CTB.exe', 'nw.exe')
    install_dir = glob.escape(util.get_game_install_path())
    if not os.path.isfile(os.path.join(install_dir, 'nw.exe')):
        url = 'https://dl.nwjs.io/v0.86.0/nwjs-v0.86.0-win-x64.zip'
        nwjs = os.path.basename(url)
        urllib.request.urlretrieve (url, nwjs)
        with zipfile.ZipFile(nwjs, 'r') as zip_ref:
            zip_ref.extractall(install_dir)
        nwjs = os.path.join(install_dir, nwjs.rsplit('.', 1)[0])
        shutil.copytree(nwjs, install_dir, dirs_exist_ok=True)
        shutil.rmtree(nwjs)
    subprocess.call([f"sed -i 's/\"frame\": true/\"frame\": false/' \"{install_dir}/package.json\""], shell=True)
