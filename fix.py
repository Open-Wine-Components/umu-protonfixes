""" Gets the game id and applies a fix if found
"""

import io
import os
import re
import sys
import urllib
import json

from importlib import import_module
from .util import check_internet
from .checks import run_checks
from .logger import log
from . import config


def get_game_id() -> str:
    """ Trys to return the game id from environment variables
    """
    if 'UMU_ID' in os.environ:
        return os.environ['UMU_ID']
    if 'SteamAppId' in os.environ:
        return os.environ['SteamAppId']
    if 'SteamGameId' in os.environ:
        return os.environ['SteamGameId']
    if 'STEAM_COMPAT_DATA_PATH' in os.environ:
        return re.findall(r'\d+', os.environ['STEAM_COMPAT_DATA_PATH'])[-1]

    log.crit('Game ID not found in environment variables')
    return None


def get_game_name() -> str:
    """ Trys to return the game name from environment variables
    """
    if 'UMU_ID' in os.environ:
        if os.path.isfile(os.environ['WINEPREFIX'] + '/game_title'):
            with open(os.environ['WINEPREFIX'] + '/game_title', 'r', encoding='utf-8') as file:
                return file.readline()

        if not check_internet():
            log.warn('No internet connection, can\'t fetch name')
            return 'UNKNOWN'

        try:
            # Fallback to 'none', if STORE isn't set
            store = os.getenv('STORE', 'none')
            url = f'https://umu.openwinecomponents.org/umu_api.php?umu_id={os.environ["UMU_ID"]}&store={store}'
            headers = {'User-Agent': 'Mozilla/5.0'}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as response:
                data = response.read()
                json_data = json.loads(data)
                title = json_data[0]['title']
            with open(os.environ['WINEPREFIX'] + '/game_title', 'w', encoding='utf-8') as file:
                file.write(title)
            return title
        except TimeoutError as ex:
            log.info('umu.openwinecomponents.org timed out')
            log.debug(f'TimeoutError occurred: {ex}')
        except OSError as ex:
            log.debug(f'OSError occurred: {ex}')
        except IndexError as ex:
            log.debug(f'IndexError occurred: {ex}')
        except UnicodeDecodeError as ex:
            log.debug(f'UnicodeDecodeError occurred: {ex}')
    else:
        try:
            game_library = re.findall(r'.*/steamapps', os.environ['PWD'], re.IGNORECASE)[-1]
            game_manifest = os.path.join(game_library, f'appmanifest_{get_game_id()}.acf')

            with io.open(game_manifest, 'r', encoding='utf-8') as appmanifest:
                for xline in appmanifest.readlines():
                    if 'name' in xline.strip():
                        name = re.findall(r'"[^"]+"', xline, re.UNICODE)[-1]
                        return name
        except OSError:
            pass
        except IndexError:
            pass
        except UnicodeDecodeError:
            pass

    return 'UNKNOWN'


def run_fix(game_id: str) -> None:
    """ Loads a gamefix module by it's gameid
    """

    if game_id is None:
        return

    if config.enable_checks:
        run_checks()

    game = f'{get_game_name()} ({game_id})'
    localpath = os.path.expanduser('~/.config/protonfixes/localfixes')

    # execute default.py
    if os.path.isfile(os.path.join(localpath, 'default.py')):
        # Ensure local gamefixes are importable as modules via PATH
        with open(os.path.join(localpath, '__init__.py'), 'a', encoding='utf-8'):
            sys.path.append(os.path.expanduser('~/.config/protonfixes'))
        try:
            game_module = import_module('localfixes.default')
            log.info('Using local defaults for ' + game)
            game_module.main()
        except ImportError:
            log.info('No local defaults found for ' + game)
    elif config.enable_global_fixes:
        try:
            if game_id.isnumeric():
                game_module = import_module('protonfixes.gamefixes-steam.default')
            else:
                log.info('Non-steam game ' + game)
                game_module = import_module('protonfixes.gamefixes-umu.default')
            log.info('Using global defaults for ' + game)
            game_module.main()
        except ImportError:
            log.info('No global defaults found')

    # execute <game_id>.py
    if os.path.isfile(os.path.join(localpath, game_id + '.py')):
        # Ensure local gamefixes are importable as modules via PATH
        with open(os.path.join(localpath, '__init__.py'), 'a', encoding='utf-8'):
            sys.path.append(os.path.expanduser('~/.config/protonfixes'))
        try:
            game_module = import_module('localfixes.' + game_id)
            log.info('Using local protonfix for ' + game)
            game_module.main()
        except ImportError:
            log.info('No local protonfix found for ' + game)
    elif config.enable_global_fixes:
        try:
            if game_id.isnumeric():
                game_module = import_module('protonfixes.gamefixes-steam.' + game_id)
            else:
                log.info('Non-steam game ' + game)
                if os.environ.get('STORE'):
                    if os.environ['STORE'].lower() == 'amazon':
                        log.info('Amazon store specified, using Amazon database')
                        game_module = import_module('protonfixes.gamefixes-amazon.' + game_id)
                    elif os.environ['STORE'].lower() == 'battlenet':
                        log.info('Battle.net store specified, using Battle.net database')
                        game_module = import_module('protonfixes.gamefixes-battlenet.' + game_id)
                    elif os.environ['STORE'].lower() == 'ea':
                        log.info('EA store specified, using EA database')
                        game_module = import_module('protonfixes.gamefixes-ea.' + game_id)
                    elif os.environ['STORE'].lower() == 'egs':
                        log.info('EGS store specified, using EGS database')
                        game_module = import_module('protonfixes.gamefixes-egs.' + game_id)
                    elif os.environ['STORE'].lower() == 'gog':
                        log.info('GOG store specified, using GOG database')
                        game_module = import_module('protonfixes.gamefixes-gog.' + game_id)
                    elif os.environ['STORE'].lower() == 'humble':
                        log.info('Humble store specified, using Humble database')
                        game_module = import_module('protonfixes.gamefixes-humble.' + game_id)
                    elif os.environ['STORE'].lower() == 'itchio':
                        log.info('Itch.io store specified, using Itch.io database')
                        game_module = import_module('protonfixes.gamefixes-itchio.' + game_id)
                    elif os.environ['STORE'].lower() == 'ubisoft':
                        log.info('Ubisoft store specified, using Ubisoft database')
                        game_module = import_module('protonfixes.gamefixes-ubisoft.' + game_id)
                    elif os.environ['STORE'].lower() == 'zoomplatform':
                        log.info('ZOOM Platform store specified, using ZOOM Platform database')
                        game_module = import_module('protonfixes.gamefixes-zoomplatform.' + game_id)
                    elif os.environ['STORE'].lower() == 'none':
                        log.info('No store specified, using umu database')
                        game_module = import_module('protonfixes.gamefixes-umu.' + game_id)
                else:
                    log.info('No store specified, using umu database')
                    game_module = import_module('protonfixes.gamefixes-umu.' + game_id)
            log.info('Using protonfix for ' + game)
            game_module.main()
        except ImportError:
            log.info('No protonfix found for ' + game)


def main() -> None:
    """ Runs the gamefix
    """
    check_args = [
        'iscriptevaluator.exe' in sys.argv[2],
        'getcompatpath' in sys.argv[1],
        'getnativepath' in sys.argv[1],
    ]

    if any(check_args):
        log.debug(str(sys.argv))
        log.debug('Not running protonfixes for setup runs')
        return

    log.info('Running protonfixes')
    run_fix(get_game_id())
