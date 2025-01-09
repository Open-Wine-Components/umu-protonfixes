import sys  # noqa: D100
from shutil import which
from trio import Path, run as async_run, open_nursery
from trio.lowlevel import open_process

EXCLUDES = ('__init__.py', 'default.py')

PROJECT = Path(__file__).parent.parent.parent

PROTON_VERB = 'waitforexitandrun'


async def run_subproc(py_bin: str, file: Path) -> None:
    """Run a module via the Python interpreter"""
    # Ensure this module is in PYTHONPATH
    path = await file.resolve(strict=True)
    proc = await open_process([py_bin, str(path), PROTON_VERB], cwd=str(path.parent))
    ret = await proc.wait()

    if ret != 0:
        err = f'The following file has an invalid import: {file}'
        raise RuntimeError(err)

    print(f"File '{file}' has valid imports")


async def main() -> None:  # noqa: D103
    """Validate import statements for files in gamefixes-*. by running them."""
    py_bin = which('python')

    if not py_bin:
        sys.exit(1)

    async with open_nursery() as nursery:
        for file in await PROJECT.rglob('gamefixes-*/*.py'):
            if file.name.startswith(EXCLUDES):
                continue
            nursery.start_soon(run_subproc, py_bin, file)


if __name__ == '__main__':
    async_run(main)
