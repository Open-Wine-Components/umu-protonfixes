""" Full Metal Daemon Muramasa
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ disables esync, disables fsync and installs xact
    """
    util.protontricks('xact')
    util.disable_esync()
    util.disable_fsync()
