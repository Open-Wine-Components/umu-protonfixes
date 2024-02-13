""" Far Cry Blood Dragon
"""
#pylint: disable=C0103

from protonfixes import util


def main():
    """ dx11 version is broken
    """

    util.set_cpu_topology_limit(24)
