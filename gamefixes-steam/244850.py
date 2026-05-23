"""Game fix for Space Engineers"""
import os

from protonfixes import util


def early() -> None:
    os.environ['PROTON_DLL_COPY'] = '*'


def main() -> None:
    util.protontricks('xaudio29')
    util.protontricks('dotnet48')
    util.protontricks('vcrun2019')

    base_attribute = '<runtime>'
    game_opts = """
    <loadFromRemoteSources enabled="true" />
    <gcServer enabled = "true" />
"""

    util.set_xml_options(base_attribute, game_opts, 'Bin64/SpaceEngineers.exe.config')
