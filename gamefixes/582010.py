""" Monster Hunter World
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Requires nvapi disabled. Needs for DX12/vkd3d
    """
    util.disable_nvapi()
    util.set_environment('VKD3D_FEATURE_LEVEL', '12_0')
