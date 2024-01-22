""" Game fix for Soulcalibur VI
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ 
    """

    # Replace launcher with game exe in proton arguments
    util.use_seccomp()
