""" Game fix for Star Citizen
"""
#pylint: disable=C0103

from protonfixes import util
import os

def main():
    """ EAC Workaround
    """
    util.set_environment('SteamGameId','starcitizen')

