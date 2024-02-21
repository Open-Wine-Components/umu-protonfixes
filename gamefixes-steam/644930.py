""" They Are Billions
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    # fix broken or missing font in UI
    util.protontricks("gdiplus")
