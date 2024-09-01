"""FarCry 3"""

from protonfixes import util


def main():
    """FarCry 3 chokes on more than 24 cores"""

    util.set_cpu_topology_limit(24)
