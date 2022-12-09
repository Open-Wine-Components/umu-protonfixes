""" Star Wars Jedi: Fallen Order
"""
#pylint: disable=C0103

from protonfixes import util
import os


def __remove_origin_install_script():
    origin_vdf_path = f"{util.get_game_install_path()}/installScript.vdf"
    if os.path.exists(origin_vdf_path):
        os.remove(origin_vdf_path)


def main():
    """ 
    """
    try:
        __remove_origin_install_script()
    except Exception:
        log("Cannot remove install script")

    # Replace launcher with game exe in proton arguments
    util.replace_command('link2ea://launchgame/1172380?platform=steam&theme=jfo', 'SwGame/Binaries/Win64/SwGame-Win64-Shipping.exe')

