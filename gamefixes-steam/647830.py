"""LEGO® Marvel Super Heroes 2"""

from protonfixes import util


def main() -> None:
    """Arena mode is unstable and likely to crash with more than 4 cores."""
    util.set_cpu_topology_limit(4)
