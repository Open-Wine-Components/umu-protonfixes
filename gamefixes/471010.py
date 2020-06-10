""" Seven: Enhanced Edition
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Seven needs DXGI=n
    """

    # https://github.com/ValveSoftware/Proton/issues/200#issuecomment-415905979
    util.set_environment('WINEDLLOVERRIDES', 'dxgi=n')
