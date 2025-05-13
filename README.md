# UMU-Protonfixes

This project acts as a stopgap for fixing games that don't work out of the box on Proton. It implements game-specific patches, such as installing Winetricks verbs.

It is the heart of `UMU-Proton` and `GE-Proton`.

## Start parameter fixes

The [default fix file for Steam](gamefixes-steam/default.py) implements a feature to install Winetricks / Protontricks verbs via startup parameters. Just add `-pf_tricks=<verb>` to it. You can install multiple verbs by adding the parameter more than once.

```bash
-pf_tricks=xliveless -pf_tricks=d3dcompiler_47
```
Additionally, you have the option to replace parts of the executable's path, such as the name of the .exe file.
Please note that all occurrences of the first part (before the '=') will be replaced. Be careful.

```bash
-pf_replace_cmd=/launcher.exe=/game.exe -pf_replace_cmd=/demo/=/full_version/
```

You can also set [dxvk options](https://github.com/doitsujin/dxvk/wiki/Configuration).

```bash
-pf_dxvk_set=dxgi.maxFrameRate=40 -pf_dxvk_set=d3d9.maxFrameRate=40
```

The order is not important and the arguments are not passed on to the game.

If you don't use `%command%` in your launch options, you can just add the parameters.

If you do, please add it after the `%command%` part, as in this example:

```bash
mangohud %command% -window -pf_replace_cmd=/launcher.exe=/game.exe -pf_tricks=xliveless
```

## Local fixes

The easiest way to implement a new fix or modify an existing one, is to use local fixes.

### Game fixes

First of all, you should find the Steam-ID of the game (right click the game in your Steam library -> 'Properties...' -> 'Updates' -> 'App ID:') and use it as the filename, with a `.py` extension.

Example `Day of Defeat: Source` (AppID 300):

> ~/.config/protonfixes/localfixes/300.py

Another type of fix is one that runs before each game. This allows you to set defaults for all games.

> ~/.config/protonfixes/localfixes/default.py

> [!IMPORTANT]
> Local fixes override the included "global" fixes.
>
> Therefore, using an existing fix could be a good starting point for modifications, since it will no longer be executed.

> [!NOTE]
> As an example, you created a local `default.py`.
>
> This overrides the "global" default fix and disables [the parameter parsing for Steam games](#start-parameter-fixes).
>
> To prevent this, copy the existing [global default file](gamefixes-steam/default.py) and modify it locally.

### Verbs

You can also add local Winetricks verbs, just like the ones implemented [here](verbs).

This also allows you to override existing Protontricks and Winetricks verbs, for example if a URL or file hash has changed.

> ~/.config/protonfixes/localfixes/<verb_name>.verb

To call them, just use the default function:

```python
util.protontricks('<verb_name>')
```

## Non-Steam games

As we support platforms other than Steam, these fixes can also be used by other launchers, such as Lutris, Heroic, Legendary or Bottles.

The current implementation requires entries in a special database that looks up the `UMU-ID`, which consists of the prefix `umu-` and in most cases the SteamID (if the game exists on that platform).

https://github.com/Open-Wine-Components/umu-database

## Config file

There is a config file located at:

> ~/.config/protonfixes/config.ini

It's not widely used at the moment, but you can configure some aspects.

### Defaults

```toml
[main]
enable_checks = true
enable_global_fixes = true

[path]
cache_dir = ~/.cache/protonfixes
```

### Variables

`enable_checks`: De-/activate checks that are run on every startup. Currently only a check if esync might cause problems.

`enable_global_fixes`: De-/activate global fixes, which are the built-in files in the `gamefix-*` folders. Only [local fixes](#local-fixes) will be executed.

`cache_dir`: Used when something needs to be unpacked or similar.

### Values

Valid "enable" values are: `yes`, `true`, `1`, `on`

Valid "disable" values are: `no`, `false`, `0`, `off`

> [!WARNING]
> Any other boolean value is invalid and will cause parsing errors.

## Building binaries

UMU-Protonfixes ships some binaries - used by some fixes - that need to be built.

These binaries are not included in this repository, but are built from git-submodules in the [subprojects folder](subprojects/). To get the submodules, run the following command:

```bash
git submodule update --init --recursive
```

To actually build the binaries, simply run:

```bash
make
```

> [!NOTE]
> You probably do not need to build them to contribute.

## Contributing

We do enforce some linting, testing and static type checking. This can and **should** be executed locally before you open a pull request.

> [!TIP]
> In order to implement a new fix, it is best practice to use [local fixes](#local-fixes).

### Pre commit hooks

We have some [pre-commit hooks](https://pre-commit.com/) in place.

> [!TIP]
> This is the easiest way to check for any mistakes that need fixing before we can accept a pull request.

Install it:

```bash
pip install pre-commit
```

or on Arch / Manjaro:

```bash
sudo pacman -Sy pre-commit
```

To set up the hook in your work directory, run the following command:

```bash
pre-commit install
```

That's it.
The hook should include everything you need and install all the necessary packages in a [virtual environment](https://docs.python.org/3/library/venv.html).

You can also run them manually, without installing the hook:

```bash
pre-commit run
# or on all files, not only staged ones:
pre-commit run --all-files
```

----------

> [!NOTE]
> All of the following information is for documentation purposes only.
>
> The preferred way to check your contribution is to use [pre-commit hooks](#pre-commit-hooks).

----------

### Fix the package name

If you clone the repository, it will default to a directory named `umu-protonfixes`.
This is not a valid name for a python module and can not be imported or executed.

You could either clone into `protonfixes` or workaround that issue with a symbolic link:

```bash
ln -rs . ../protonfixes
```

> [!TIP]
> You can also clone / copy / link the project directly into a GE-Proton used by Steam.
>
> Example: `~/.local/share/Steam/compatibilitytools.d/GE-Proton10-1/protonfixes`
>
> Run the game with the correct Proton version and you can test your changes under realistic conditions.
>
> Start `steam` from a terminal to follow the logging of `umu-protonfixes`.

### Linting

To install the necessary tools, just run:

```bash
python -m pip install --upgrade pip
pip install ruff
```

On Arch / Manjaro, you should run this instead:

```bash
sudo pacman -Sy ruff
```

To run a check, just execute:

```bash
ruff check .
```

You are good to go when you see the message `All checks passed!`.

If not, try letting `ruff` (the linter we use) fix it automatically:

```bash
ruff format .
```

### Static type checking

We use [Pyright](https://microsoft.github.io/pyright/) for type checking.

```bash
python -m pip install --upgrade pip
pip install pyright
```
On Arch / Manjaro you can install it as a system package:

```bash
sudo pacman -Sy pyright
```

Occasionally Pyright shows a warning, that you should use the latest version. You can force it to do so by running it like this:

```bash
PYRIGHT_PYTHON_FORCE_VERSION=latest pyright
```

### Testing

The filenames of the fixes are checked against the Steam and GOG APIs. All symbolic links are also checked. This is not mandatory to run locally, as you should have a working game fix to begin with, and it will be done automatically by Github's CI.

You can still run it though:

```bash
cd .github/scripts
python check_gamefixes.py
python check_imports.py
python check_verbs.py
```

You need the following prerequisites for these checks:

```bash
python -m pip install --upgrade pip
pip install ijson trio "steam[client]"
```

On Arch / Manjaro with installed `yay`:

```bash
sudo pacman -Sy python-ijson python-trio
sudo yay -Sy python-steam
```

### Unit tests

You can also manually run the [unit tests](/protonfixes_test.py). This requires the [fixed package name](#fix-the-package-name).

```bash
cd ..
python -m protonfixes.protonfixes_test
```
