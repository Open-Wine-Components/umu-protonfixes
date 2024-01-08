""" UNCHARTED: Legacy of Thieves Collection
"""
#pylint: disable=C0103

from protonfixes import util


def main():
    """ The game chokes on more than 16 cores
    """

    util.set_cpu_topology_limit(16)
