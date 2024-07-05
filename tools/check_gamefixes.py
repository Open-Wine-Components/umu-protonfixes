# pylint: disable=C0114
from pathlib import Path
from urllib.request import urlopen, Request
from http.client import HTTPSConnection
from typing import Any, Iterator, TypedDict, Union

import ijson

# Represents a valid API endpoint, where the first element is the host, second
# is the url (e.g., store.steampowered.com and store.steampowered.com). The API
# endpoint will be used to validate local gamefix modules IDs against. Assumes
# that the API is associated to the gamefix directory when passed to a function
ApiEndpoint = tuple[str, str]


# Represents a record in the UMU database
# e.g.,:
# {
#   "title": "Age of Wonders",
#   "umu_id": "umu-61500",
#   "acronym": "aow",
#   "codename": "1207658883",
#   "store": "gog",
#   "notes": null
# }
class UMUEntry(TypedDict):  # pylint: disable=C0115
    title: str
    umu_id: str
    acronym: str
    # Unique ID for the title defined in its store
    codename: str
    store: str
    notes: Union[None, str]


headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Accept": "application/font-woff2;q=1.0,application/font-woff;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# Steam games that are no longer on sale, but are valid IDs
whitelist_steam = {231990, 4730, 105400}


def check_steamfixes(project: Path, url: str, api: ApiEndpoint) -> None:
    """Verifies if the name of Steam gamefix modules are valid entries.

    Raises a ValueError if the ID is not found upstream
    """
    appids = set()

    # Get all IDs
    for file in project.joinpath("gamefixes-steam").glob("*"):
        appid = file.name.removesuffix(".py")
        if not appid.isnumeric():
            continue
        appids.add(int(appid))

    # Check the IDs against ours
    with urlopen(Request(url, headers=headers), timeout=500) as r:
        for obj in ijson.items(r, "applist.apps.item"):
            if obj["appid"] in appids:
                appids.remove(obj["appid"])
            if not appids:
                break

    # Double check that the ID is valid. It's possible that it is but
    # wasn't returned from the api in `url` for some reason
    if appids:
        host, endpoint = api
        conn = HTTPSConnection(host)

        for appid in appids.copy():
            conn.request("GET", f"{endpoint}{appid}")
            r = conn.getresponse()
            parser: Iterator[tuple[str, str, Any]] = ijson.parse(r)

            for prefix, _, value in parser:
                if prefix == f"{appid}.success" and isinstance(value, bool) and value:
                    appids.remove(appid)
                    break
                if not appids:
                    break

            r.read()

        conn.close()

    for appid in appids:
        if appid not in whitelist_steam:
            err = f"Steam app id is invalid: {appid}"
            raise ValueError(err)


def check_gogfixes(project: Path, url: str, api: ApiEndpoint) -> None:
    """Verifies if the name of GOG gamefix modules are valid entries.

    Raises a ValueError if the ID is not found upstream, in gamefixes-steam
    or in the umu-database
    """
    appids = set()

    # Find all IDs in batches of 50. The gog api enforces 50 ids per request
    # See https://gogapidocs.readthedocs.io/en/latest/galaxy.html#get--products
    for gogids in _batch_generator(project.joinpath("gamefixes-gog")):
        sep = "%2C"  # Required comma separator character. See the docs.
        appids = gogids.copy()

        with urlopen(
            Request(f"{url}{sep.join(appids)}", headers=headers), timeout=500
        ) as r:
            for obj in ijson.items(r, "item"):
                # Like Steam's, app ids are integers
                if (appid := str(obj["id"])) in appids:
                    appids.remove(appid)
                if not appids:
                    break

    # IDs may be links to Steam fixes.
    if appids:
        for file in project.joinpath("gamefixes-steam").glob("*"):
            if (appid := file.name.removesuffix(".py")) in appids:
                appids.remove(appid)
            if not appids:
                break

    # IDs may not be using upstream's ID (e.g., Alien Breed). Check all ids against the umu database
    if appids:
        host, endpoint = api
        conn = HTTPSConnection(host)
        conn.request("GET", endpoint)
        r = conn.getresponse()

        for _ in ijson.items(r, "item"):
            obj: UMUEntry = _
            if (appid := str(obj["umu_id"]).removeprefix("umu-")) in appids:
                appids.remove(appid)
            if not appids:
                break

        conn.close()

    if appids:
        err = (
            "The following GOG app ids are invalid or are missing entries"
            f" in the umu database: {appids}"
        )
        raise ValueError(err)


def _batch_generator(gamefix: Path, size=50) -> set[str]:
    appids = set()
    # Keep track of the count because some APIs enforce limits
    count = 0

    # Process only umu-* app ids
    for file in gamefix.glob("*"):
        appid = file.name.removeprefix("umu-").removesuffix(".py")
        appids.add(appid)
        if count == size:
            yield appids
            appids.clear()
            count = 0
            continue
        count += 1

    yield appids


def main() -> None:
    """Validate gamefixes modules."""
    # Top-level project directory that is expected to contain gamefix directories
    project = Path(__file__).parent.parent

    # Steam API to acquire a single id. Used as fallback in case some IDs could
    # not be validated. Unforutnately, this endpoint does not accept a comma
    # separated list of IDs so we have to make one request per ID after making
    # making a request to `api.steampowered.com`.
    # NOTE: There's neither official nor unofficial documentation. Only forum posts
    # See https://stackoverflow.com/questions/46330864/steam-api-all-games
    steamapi: ApiEndpoint = ("store.steampowered.com", "/api/appdetails?appids=")

    # UMU Database, that will be used to validate umu gamefixes ids against
    # See https://github.com/Open-Wine-Components/umu-database/blob/main/README.md
    umudb_gog: ApiEndpoint = ("umu.openwinecomponents.org", "/umu_api.php?store=gog")

    # Steam API
    # Main API used to validate steam gamefixes
    # NOTE: There's neither official nor unofficial documentation. Only forum posts
    # See https://stackoverflow.com/questions/46330864/steam-api-all-games
    steampowered = (
        "https://api.steampowered.com/ISteamApps/GetAppList/v0002/?format=json"
    )

    # GOG API
    # See https://gogapidocs.readthedocs.io/en/latest/galaxy.html#get--products
    gogapi = "https://api.gog.com/products?ids="

    check_steamfixes(project, steampowered, steamapi)
    check_gogfixes(project, gogapi, umudb_gog)


if __name__ == "__main__":
    main()
