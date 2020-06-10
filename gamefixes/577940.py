""" Killer Instinct
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ d9vk breaks with it and dxgi. Use wined3d for now.
    """

    util.set_environment('PROTON_USE_WINED3D','1')
