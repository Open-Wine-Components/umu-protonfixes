""" Game fix for The Forest
"""

# pylint: disable=C0103

from protonfixes import util


def main():
    """ If SMT/HT is enabled, The Forest runs with extremely choppy. Just bad.
        We can fix it by setting the topology to the physical cores / core count.
        TODO: This fix was not tested with more than 10 physical cores yet.
    """
    util.set_cpu_topology_nosmt()
