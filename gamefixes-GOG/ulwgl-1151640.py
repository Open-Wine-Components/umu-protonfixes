""" Game fix for Horizon Zero Dawn
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """
    """

    # C++ runtime is not provided in the manifest
    util.protontricks('vcrun2019')
