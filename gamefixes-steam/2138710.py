"""Sifu"""

from protonfixes import util, BasePath


def main() -> None:
    """Stops the game from freezing."""
    util.set_ini_options('[/script/engine.renderersettings]\nr.CreateShadersOnLoad=1', 'Sifu/Saved/Config/WindowsClient/Engine.ini', base_path = BasePath.APPDATA_LOCAL)
