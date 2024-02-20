""" Gets the game id and applies a fix if found
"""

from __future__ import print_function
import io
import os
import re
import sys
import urllib
import json
from importlib import import_module
from .util import protonprefix
from .checks import run_checks
from .logger import log
from . import config

def game_id():
    """ Trys to return the game id from environment variables
    """
    if 'ULWGL_ID' in os.environ:
        return os.environ['ULWGL_ID']
    if 'SteamAppId' in os.environ:
        return os.environ['SteamAppId']
    if 'SteamGameId' in os.environ:
        return os.environ['SteamGameId']
    if 'STEAM_COMPAT_DATA_PATH' in os.environ:
        return re.findall(r'\d+', os.environ['STEAM_COMPAT_DATA_PATH'])[-1]

    log.crit('Game ID not found in environment variables')
    return None


def game_name():
    """ Trys to return the game name from environment variables
    """
    if 'ULWGL_ID' in os.environ:
        if os.path.isfile(os.environ['WINEPREFIX'] + "/game_title"):
            with open(os.environ['WINEPREFIX'] + "/game_title", 'r') as file:
                return file.readline()
        else:
            try:
                if 'STORE' in os.environ:
                    url = "https://ulwgl.openwinecomponents.org/ulwgl_api.php?ulwgl_id=" + os.environ['ULWGL_ID'] + "&store=" + os.environ['STORE']
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    req = urllib.request.Request(url, headers=headers)
                    response = urllib.request.urlopen(req)
                    data = response.read()
                    json_data = json.loads(data)
                    title = json_data[0]['title']
                    file = open(os.environ['WINEPREFIX'] + "/game_title", 'w')
                    file.write(title)
                    file.close()
                else:
                    url = "https://ulwgl.openwinecomponents.org/ulwgl_api.php?ulwgl_id=" + os.environ['ULWGL_ID'] + "&store=none"
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    req = urllib.request.Request(url, headers=headers)
                    response = urllib.request.urlopen(req)
                    data = response.read()
                    json_data = json.loads(data)
                    title = json_data[0]['title']
                    file = open(os.environ['WINEPREFIX'] + "/game_title", 'w')
                    file.write(title)
                    file.close()
            except OSError as e:
                #log.info('OSError occurred: {}'.format(e))  # used for debugging
                return 'UNKNOWN'
            except IndexError as e:
                #log.info('IndexError occurred: {}'.format(e))  # used for debugging
                return 'UNKNOWN'
            except UnicodeDecodeError as e:
                #log.info('UnicodeDecodeError occurred: {}'.format(e))  # used for debugging
                return 'UNKNOWN'
            with open(os.environ['WINEPREFIX'] + "/game_title", 'r') as file:
                return file.readline()
    else:
        try:
            game_library = re.findall(r'.*/steamapps', os.environ['PWD'], re.IGNORECASE)[-1]
            game_manifest = os.path.join(game_library, 'appmanifest_' + game_id() + '.acf')

            with io.open(game_manifest, 'r', encoding='utf-8') as appmanifest:
                for xline in appmanifest.readlines():
                    if 'name' in xline.strip():
                        name = re.findall(r'"[^"]+"', xline, re.UNICODE)[-1]
                        return name
        except OSError:
            return 'UNKNOWN'
        except IndexError:
            return 'UNKNOWN'
        except UnicodeDecodeError:
            return 'UNKNOWN'
    return 'UNKNOWN'


def run_fix(gameid):
    """ Loads a gamefix module by it's gameid
    """

    if gameid is None:
        return

    if config.enable_checks:
        run_checks()

    game = game_name() + ' ('+ gameid + ')'
    localpath = os.path.expanduser('~/.config/protonfixes/localfixes')

    # execute default.py
    if os.path.isfile(os.path.join(localpath, 'default.py')):
        open(os.path.join(localpath, '__init__.py'), 'a').close()
        sys.path.append(os.path.expanduser('~/.config/protonfixes'))
        try:
            game_module = import_module('localfixes.default')
            log.info('Using local defaults for ' + game)
            game_module.main()
        except ImportError:
            log.info('No local defaults found for ' + game)
    elif config.enable_global_fixes:
        try:
            if gameid.isnumeric():
                game_module = import_module('protonfixes.gamefixes-steam.default')
            else:
                log.info('Non-steam game ' + game)
                game_module = import_module('protonfixes.gamefixes-ulwgl.default')
            log.info('Using global defaults for ' + game)
            game_module.main()
        except ImportError:
            log.info('No global defaults found')

    # execute <gameid>.py
    if os.path.isfile(os.path.join(localpath, gameid + '.py')):
        open(os.path.join(localpath, '__init__.py'), 'a').close()
        sys.path.append(os.path.expanduser('~/.config/protonfixes'))
        try:
            game_module = import_module('localfixes.' + gameid)
            log.info('Using local protonfix for ' + game)
            game_module.main()
        except ImportError:
            log.info('No local protonfix found for ' + game)
    elif config.enable_global_fixes:
        try:
            if gameid.isnumeric():
                game_module = import_module('protonfixes.gamefixes-steam.' + gameid)
            else:
                log.info('Non-steam game ' + game)
                if 'STORE' in os.environ:
                  if os.environ['STORE'].lower() == "amazon":
                    log.info('Amazon store specified, using Amazon database')
                    game_module = import_module('protonfixes.gamefixes-amazon.' + gameid)
                  elif os.environ['STORE'].lower() == "battlenet":
                    log.info('Battle.net store specified, using Battle.net database')
                    game_module = import_module('protonfixes.gamefixes-battlenet.' + gameid)
                  elif os.environ['STORE'].lower() == "ea":
                    log.info('EA store specified, using EA database')
                    game_module = import_module('protonfixes.gamefixes-ea.' + gameid)
                  elif os.environ['STORE'].lower() == "egs":
                    log.info('EGS store specified, using EGS database')
                    game_module = import_module('protonfixes.gamefixes-egs.' + gameid)
                  elif os.environ['STORE'].lower() == "gog":
                    log.info('GOG store specified, using GOG database')
                    game_module = import_module('protonfixes.gamefixes-gog.' + gameid)
                  elif os.environ['STORE'].lower() == "humble":
                    log.info('Humble store specified, using Humble database')
                    game_module = import_module('protonfixes.gamefixes-humble.' + gameid)
                  elif os.environ['STORE'].lower() == "itchio":
                    log.info('Itch.io store specified, using Itch.io database')
                    game_module = import_module('protonfixes.gamefixes-itchio.' + gameid)
                  elif os.environ['STORE'].lower() == "ubisoft":
                    log.info('Ubisoft store specified, using Ubisoft database')
                    game_module = import_module('protonfixes.gamefixes-ubisoft.' + gameid)
                  elif os.environ['STORE'].lower() == "zoomplatform":
                    log.info('ZOOM Platform store specified, using ZOOM Platform database')
                    game_module = import_module('protonfixes.gamefixes-zoomplatform.' + gameid)
                  elif os.environ['STORE'].lower() == "none":
                    log.info('No store specified, using ULWGL database')
                    game_module = import_module('protonfixes.gamefixes-ulwgl.' + gameid)
                else:
                  log.info('No store specified, using ULWGL database')
                  game_module = import_module('protonfixes.gamefixes-ulwgl.' + gameid)
            log.info('Using protonfix for ' + game)
            game_module.main()
        except ImportError:
            log.info('No protonfix found for ' + game)


def main():
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
    run_fix(game_id())
