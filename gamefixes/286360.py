""" Shadows on the Vatican - Act I: Greed
Launcher keeps it's process running in the background but nothing shows up
"""
#pylint: disable=C0103

from protonfixes import util, os

def main():
    util.replace_command('SotV_Launcher.exe', 'hd/SotV1.exe')
    os.chdir('hd') 
