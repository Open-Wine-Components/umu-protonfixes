""" Witcher 2
"""
#pylint: disable=C0103

from protonfixes import util


def main():
    """ Witcher 2 chokes on more than 31 cores
    """

    util.set_cpu_topology_limit(31)
