"""Game fix for Flowers - Le Volume Sur Printemps

This fix installs the font that should be bundled with the game. Without this
fix, the default font will be used which doesn't wrap correctly, resulting in
the text breaking outside its text box area.
"""

import os
import __main__ as protonmain
from hashlib import sha256
from subprocess import run
from protonfixes import util
from protonfixes.logger import log


def main():
    env = protonmain.g_session.env.copy()
    wine = f"{util.protondir()}/files/bin/wine64"
    install_dir = util.get_game_install_path()

    # Font installer inside the `fonts` subdir
    font_installer = "overlock_mod_font_installer.exe"

    # Digest of the font installer
    hashsum = "d3bd48162d91322c3d2861cdccc538955336eff7f0fe50eeafee1b7551a52152"

    if os.path.isfile(f"{util.protonprefix()}/drive_c/windows/Fonts/Overlock-Mod.ttf"):
        log.info("Overlock-Mod.ttf already installed in prefix")
        return

    if not os.path.isfile(f"{install_dir}/font/{font_installer}"):
        log.warn(f"Could not find '{font_installer}' in '{install_dir}', skipping...")
        return

    with open(f"{install_dir}/font/{font_installer}", mode="rb") as file:
        if sha256(file.read()).hexdigest() != hashsum:
            log.warn(f"Digest mismatched: {font_installer}")
            log.warn(f"Expected '{hashsum}', skipping...")
            return

    # Run the font installer. Unfortunately a small window should popup...
    # and it doesn't seem like there's a way around that
    log.info("Installing font 'Overlock-Mod.ttf' in prefix")

    # Ensure DISPLAY=:0 to ensure we do not crash when running the installer
    # when using gamescope
    env["DISPLAY"] = ":0"

    retc = run(
        [
            wine,
            "start",
            "/unix",
            f"{install_dir}/font/{font_installer}",
        ],
        check=False,
        env=env,
    ).returncode

    if retc:
        log.warn(f"Running '{font_installer}' exited with the status code: {retc}")
