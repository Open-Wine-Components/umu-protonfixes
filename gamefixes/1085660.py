""" Game fix Destiny 2
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    # Requires vcrun2019 to launch
    util.protontricks('vcrun2019_ge')
    util.set_environment('WINEDLLOVERRIDES','dxgi=n')
