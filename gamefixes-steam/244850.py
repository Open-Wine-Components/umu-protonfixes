""" Game fix for Space Engineers
"""

# pylint: disable=C0103

from protonfixes import util


def main():

    base_attibutte = "<runtime>"
    game_opts = """
  	<gcServer enabled = "true" />
"""

    util.set_xml_options(base_attibutte, game_opts, 'SpaceEngineers.exe.config','game')

    util.append_argument('-skipintro')
