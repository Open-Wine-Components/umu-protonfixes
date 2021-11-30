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

    # This requires Proton 5.0 installed
    util.protontricks_proton_5('dotnet48')
    util.append_argument('-skipintro')
