""" APB Reloaded: Fix Wrong DLL error and Steam login crash
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    # Install Visual C++ Runtime 2017
    util.protontricks('vcrun2017')
