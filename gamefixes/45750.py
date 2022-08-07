""" Game fix for Lost Planet 2 (2010)
This game requires two fixes to work:
1. A mocked xlive.dll for GFWL (multiplayer will not work, but the single player does)
2. No more than 12 CPU cores (on PCGamingWiki is described as 6, but on my personal test I was able to set until 12 of 16) [source: https://www.pcgamingwiki.com/wiki/Lost_Planet_2#Alternate_solution_for_high_core_CPUs]
"""
#pylint: disable=C0103
import os
import hashlib
import urllib.request
import multiprocessing
import shutil
from pathlib import Path

from protonfixes import util
from protonfixes.logger import log

xlive_url = "https://github.com/ThirteenAG/Ultimate-ASI-Loader/releases/download/v4.68/Ultimate-ASI-Loader.zip"
custom_xlivedll_sha256 = "baba99929487b005bb9b168acfd852550055f22e5f1059c9032765209bb185e5"


def get_sha256(filepath: str) -> str:
    try:
        with open(filepath,"rb") as f:
            return hashlib.sha256(f.read()).hexdigest();
    except FileNotFoundError:
        log(f"File '{filepath}' could not be found")


def download_custom_xlive_dll():
    xlive_path = f"{util.get_game_install_path()}/xlive.dll"
    compressed_filepath = f"{util.get_game_install_path()}/xlive.zip"

    if not os.path.exists(xlive_path):
        if os.path.exists(compressed_filepath):
            os.remove(compressed_filepath)

        log("Downloading mocked 'xlive.dll'")
        urllib.request.urlretrieve(xlive_url, compressed_filepath)

        shutil.unpack_archive(compressed_filepath, extract_dir=util.get_game_install_path())

        extracted_file = f"{util.get_game_install_path()}/dinput8.dll"

        if get_sha256(extracted_file) != custom_xlivedll_sha256:
            log("Mocked 'xlive.dll' has an unexpected checksum. It will be removed.")
            os.remove(extracted_file)
        else:
            shutil.move(extracted_file, xlive_path)

        os.remove(compressed_filepath)

    else:
        if get_sha256(xlive_path) != custom_xlivedll_sha256:
            log("'xlive.dll' has an unexpected checksum. It will be redowloaded.")
            os.remove(xlive_path)
            download_custom_xlive_dll()  # try to redownload once


def main():
    try:
        download_custom_xlive_dll()
    except:
        log("Unexpected exception when downloading mocked 'xlive.dll'")

    # the core fix is only applied if the user has not provided its own topology mapping
    if not os.getenv("WINE_CPU_TOPOLOGY"):
        try:
            cpu_cores = multiprocessing.cpu_count()
        except:
            cpu_cores = 0
            log("Could not retrieve the number of CPU cores")

        if cpu_cores > 12:
            util.set_environment("WINE_CPU_TOPOLOGY", f"12:{','.join(str(n) for n in range(12))}")


