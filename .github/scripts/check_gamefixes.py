"""This provides a check, if all filenames are correct and if all IDs used by GOG and Steam fixes are valid."""

import sys
from pathlib import Path
from urllib.request import urlopen, Request
from http.client import HTTPSConnection
from typing import Any
from collections.abc import Generator

import ijson

from steam_client import Steam

# Represents a valid API endpoint, where the first element is the host, second
# is the url (e.g., store.steampowered.com and store.steampowered.com). The API
# endpoint will be used to validate local gamefix modules IDs against. Assumes
# that the API is associated to the gamefix directory when passed to a function
ApiEndpoint = tuple[str, str]


headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0',
    'Accept': 'application/font-woff2;q=1.0,application/font-woff;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}


def check_steamfixes(project: Path) -> None:
    """Verifies if the name of Steam gamefix modules are valid entries.

    Raises a ValueError if the ID is not found upstream
    """
    steam = Steam()

    invalid_appids = set()

    for appids in _batch_generator(project.joinpath('gamefixes-steam'), 50):
        # If no more ids are produced by the generator, stop processing.
        if not appids:
            continue

        appids = {int(x) for x in appids}
        steam_appids = steam.get_valid_appids(appids)

        # If an ID doesn't exist in the Steam result then it's invalid
        invalid_appids.update(appids - steam_appids)

    if invalid_appids:
        err = f'The following Steam app ids are invalid: {invalid_appids}'
        raise ValueError(err)


def check_gogfixes(project: Path, url: str, api: ApiEndpoint) -> None:
    """Verifies if the name of GOG gamefix modules are valid entries.

    Raises a ValueError if the ID is not found upstream, in gamefixes-steam
    or in the umu-database
    """
    appids = set()

    # Find all IDs in batches of 50. The gog api enforces 50 ids per request
    # See https://gogapidocs.readthedocs.io/en/latest/galaxy.html#get--products
    for gogids in _batch_generator(project.joinpath('gamefixes-gog')):
        # If no more ids are produced by the generator, stop processing.
        if not gogids:
            continue

        sep = '%2C'  # Required comma separator character. See the docs.
        appids = gogids.copy()

        print(f'Validating GOG app ids against "{url}"...', file=sys.stderr)
        with urlopen(
            Request(f'{url}{sep.join(appids)}', headers=headers), timeout=500
        ) as r:
            for obj in ijson.items(r, 'item'):
                # Like Steam's, app ids are integers
                if (appid := str(obj['id'])) in appids:
                    print(f'Removing GOG app id: "{appid}"', file=sys.stderr)
                    appids.remove(appid)
                if not appids:
                    break

    # IDs may be links to Steam fixes.
    if appids:
        print('Validating GOG app ids against Steam app ids...', file=sys.stderr)
        for file in project.joinpath('gamefixes-steam').glob('*'):
            if (appid := file.name.removesuffix('.py')) in appids:
                print(f'Removing GOG app id: "{appid}"', file=sys.stderr)
                appids.remove(appid)
            if not appids:
                break

    # IDs may not be using upstream's ID (e.g., Alien Breed). Check all ids against the umu database
    if appids:
        host, endpoint = api
        conn = HTTPSConnection(host)
        conn.request('GET', endpoint)
        r = conn.getresponse()

        print(f'Validating GOG app ids against "{host}"...', file=sys.stderr)
        for obj in ijson.items(r, 'item'):
            if (appid := str(obj['umu_id']).removeprefix('umu-')) in appids:
                print(f'Removing GOG app id: "{appid}"', file=sys.stderr)
                appids.remove(appid)
            if not appids:
                break

        conn.close()

    print(f'Remaining GOG app ids: {appids}', file=sys.stderr)
    if appids:
        err = (
            'The following GOG app ids are invalid or are missing entries'
            f' in the umu database: {appids}'
        )
        raise ValueError(err)


def _batch_generator(gamefix: Path, size: int = 50) -> Generator[set[str], Any, Any]:
    is_steam = 'gamefixes-steam' in gamefix.name
    appids = set()
    # Keep track of the count because some APIs enforce limits
    count = 0

    # Process only umu-* app ids
    for file in gamefix.glob('*'):
        if not file.name.startswith('umu-') and not is_steam:
            continue

        appid = file.name.removeprefix('umu-').removesuffix('.py')
        if is_steam and not appid.isnumeric():
            continue

        count += 1
        appids.add(appid)
        if count == size:
            yield appids
            appids.clear()
            count = 0
            continue

    yield appids


def check_links(root: Path) -> None:
    """Check for broken symbolic links"""
    gamefixes = [
        file
        for file in root.glob('gamefixes-*/*.py')
        if not file.name.startswith(('__init__.py', 'default.py', 'winetricks-gui.py'))
    ]

    print('Checking for broken symbolic links...', file=sys.stderr)
    for module in gamefixes:
        print(f'{module.parent.name}/{module.name}', file=sys.stderr)
        if module.is_symlink() and not module.exists():
            err = f'The following file is not a valid symbolic link: {module}'
            raise FileNotFoundError(err)


def check_filenames(root: Path) -> None:
    """Check for expected file names.

    All files in non-steam gamefixes are expected to start with 'umu-'
    All files in steam gamefixes are expected to have a numeric name
    """
    gamefixes = [
        file
        for file in root.glob('gamefixes-*/*.py')
        if not file.name.startswith(('__init__.py', 'default.py', 'winetricks-gui.py'))
    ]

    print('Checking for expected file names...', file=sys.stderr)
    for module in gamefixes:
        print(f'{module.parent.name}/{module.name}', file=sys.stderr)
        is_steam = module.parent.name.startswith('gamefixes-steam')
        if not module.exists():
            err = f'The following file does not exist: {module.parent.name}/{module}'
            raise FileNotFoundError(err)
        elif is_steam and not module.stem.isnumeric():
            err = f'The following Steam fix filename is invalid: {module}'
            raise ValueError(err)
        elif not is_steam and not module.name.startswith('umu-'):
            err = f'The following file does not start with "umu-": {module}'
            raise ValueError(err)


def main() -> None:
    """Validate gamefixes modules."""
    # Top-level project directory that is expected to contain gamefix directories
    project = Path(__file__).parent.parent.parent
    print(project)

    # UMU Database, that will be used to validate umu gamefixes ids against
    # See https://github.com/Open-Wine-Components/umu-database/blob/main/README.md
    umudb_gog: ApiEndpoint = ('umu.openwinecomponents.org', '/umu_api.php?store=gog')

    # GOG API
    # See https://gogapidocs.readthedocs.io/en/latest/galaxy.html#get--products
    gogapi = 'https://api.gog.com/products?ids='

    check_links(project)
    check_filenames(project)
    check_steamfixes(project)
    check_gogfixes(project, gogapi, umudb_gog)


if __name__ == '__main__':
    main()
