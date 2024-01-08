""" Game fix for Lost Planet 2 (2010)
This game requires two fixes to work:
1. A mocked xlive.dll for GFWL (multiplayer will not work, but the single player does)
2. No more than 12 CPU cores (on PCGamingWiki is described as 6, but on my personal test I was able to set until 12 of 16) [source: https://www.pcgamingwiki.com/wiki/Lost_Planet_2#Alternate_solution_for_high_core_CPUs]
"""

#pylint: disable=C0103

import os
import multiprocessing

from protonfixes import util


def main():
    util.protontricks("xliveless")

    # the core fix is only applied if the user has not provided its own topology mapping
    if not os.getenv("WINE_CPU_TOPOLOGY"):
        try:
            cpu_cores = multiprocessing.cpu_count()
        except:
            cpu_cores = 0
            log("Could not retrieve the number of CPU cores")

        if cpu_cores > 12:
            util.set_environment("WINE_CPU_TOPOLOGY", f"12:{','.join(str(n) for n in range(12))}")


