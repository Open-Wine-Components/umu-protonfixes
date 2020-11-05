""" Game fix for Divinity Original Sin 2
"""
#pylint: disable=C0103

import os
import shutil
import subprocess
from protonfixes import util
from protonfixes import splash

def main():
    """ Launcherfix
    """

    installpath = os.path.abspath(os.path.join(os.getcwd(), os.pardir))


    if not os.path.isfile(os.path.join(os.path.abspath(installpath), 'bin', 'EoCApp.exe')):

        if not os.path.isdir(os.path.join(os.path.abspath(installpath), 'bin-bak')):
            shutil.move(os.path.join(os.path.abspath(installpath), 'bin'), os.path.join(os.path.abspath(installpath), 'bin-bak'))
            subprocess.call(['ln', '-s', os.path.join(os.path.abspath(installpath), 'DefEd', 'bin'), os.path.join(os.path.abspath(installpath), 'bin')])

        if not os.path.isdir(os.path.join(os.path.abspath(installpath), 'Data-bak')):
            shutil.move(os.path.join(os.path.abspath(installpath), 'Data'), os.path.join(os.path.abspath(installpath), 'Data-bak'))
            subprocess.call(['ln', '-s', os.path.join(os.path.abspath(installpath), 'DefEd', 'Data'), os.path.join(os.path.abspath(installpath), 'Data')])

    util.replace_command('SupportTool.exe', 'EoCApp.exe')

