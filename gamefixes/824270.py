""" KovaaKs: Fix missing C++ runtime
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    util.protontricks('vcrun2019_ge')
