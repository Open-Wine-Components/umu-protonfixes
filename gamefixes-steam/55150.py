""" Warhammer 40,000: Space Marine - Anniversary Edition
"""
#pylint: disable=C0103

from protonfixes import util


def main():
    """ Space Marine chokes on more than 24 cores
    """
    util.set_cpu_topology_limit(24)
