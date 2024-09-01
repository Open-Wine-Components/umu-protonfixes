"""Game fix for New World"""

from protonfixes import util


def main():
    """Needs core count limit"""
    # Fix the startup process:
    util.set_cpu_topology_limit(12)
