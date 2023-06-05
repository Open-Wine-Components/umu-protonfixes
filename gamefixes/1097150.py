""" Game fix for Fall Guys
"""
#pylint: disable=C0103
from protonfixes import util

def main():
    """ Create symlink of eac so at the right location
    """
    util.install_eac_runtime()
    util.disable_esync()
    util.disable_fsync()

