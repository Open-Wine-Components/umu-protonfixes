""" Gobliiins 5
Setup doesn't work and language is default to french
"""
#pylint: disable=C0103

import os
import sys
import subprocess
import glob
from protonfixes import util

def main():
    if sys.argv[2].find("winsetup")!=-1:
        os.chdir(sys.argv[2][-29:-13])

    install_dir = glob.escape(util.get_game_install_path())
    with open(os.path.join(install_dir,'Gobliiins5-Part4/acsetup.cfg'), 'r', encoding='utf-8') as f:
        if 'Linear' not in f.read():
            for i in range(1,5):
                subprocess.call([f"sed -i 's/filter=stdscale/filter=Linear/' {install_dir}/Gobliiins5-Part{i}/acsetup.cfg"], shell=True)
                subprocess.call([f"sed -i 's/translation.*/translation=English/' {install_dir}/Gobliiins5-Part{i}/acsetup.cfg"], shell=True)
