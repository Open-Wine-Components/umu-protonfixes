""" TOXIKK
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ d9vk breaks with it and dxgi. Use wined3d for now.
    """

    util.set_environment('WINEDLLOVERRIDES','dxgi=n')
