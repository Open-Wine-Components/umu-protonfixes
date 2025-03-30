"""Monster Hunter Wilds"""

import os
from protonfixes import util


def main() -> None:
    """Imports Monster Hunter: World save from remote steam cloud folder. We need to get steam cloud ID, not steamID, which is only reported as folder name in local"""
    # get all remote IDs to anticipate for multi accounts
    listRemoteID = [
        name for name in os.listdir(f'{os.environ["STEAM_BASE_FOLDER"]}/userdata')
    ]

    # import save for all remote IDs because we don't know which one is the right ID. import function is robust enough to anticipate wrong ID.
    for accoundID in listRemoteID:
        # skip 0
        if accoundID != '0':
            util.import_saves_folder(
                582010, f'../../Program Files (x86)/Steam/userdata/{accoundID}/582010/'
            )
