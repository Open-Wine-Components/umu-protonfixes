"""Ship Graveyard Simulator Prologue"""

from protonfixes import util


def main():
    """needs builtin vulkan-1"""

    util.winedll_override('vulkan-1', 'b')
