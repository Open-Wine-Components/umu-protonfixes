"""The Blind Prophet
garbled fonts & No cursive font (Segoe Script)
"""

from .. import util


def main() -> None:
    util.winedll_override('d3d9', '')
    util.protontricks('segoe_script')
