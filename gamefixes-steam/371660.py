"""Far Cry Primal"""

from protonfixes import util


def main():
    """chokes on more than 31 cores"""

    util.set_cpu_topology_limit(31)
