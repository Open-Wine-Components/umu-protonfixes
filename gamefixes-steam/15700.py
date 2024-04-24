""" Oddworld: Abe's Oddysee
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    util.protontricks('cnc_ddraw') # Videos are laggy without this
