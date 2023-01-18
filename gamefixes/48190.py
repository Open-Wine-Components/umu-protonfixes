""" Game fix for Assassin's Creed: Brotherhood

Game uses an old customized Ubisoft launcher that's currently not working with Proton.
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    util.append_argument('-playoffline')
