import sys  # noqa: D100
from pathlib import Path
from asyncio import run as run_async, create_subprocess_exec, gather
from shutil import which

EXCLUDES = ('__init__.py', 'default.py')

PROJECT = Path(__file__).parent.parent.parent


async def run_subproc(py_bin: str, file: Path) -> tuple[int, Path]:
    """Run a module via the Python interpreter"""
    # Ensure this module is in PYTHONPATH
    args = file.resolve(strict=True)
    proc = await create_subprocess_exec(
        py_bin, args, cwd=args.parent, env={'PYTHONPATH': str(PROJECT.parent)}
    )
    ret = await proc.wait()
    return ret, file


async def main() -> None:  # noqa: D103
    """Validate import statements for files in gamefixes-*. by running them."""
    files = filter(
        lambda file: not file.name.startswith(EXCLUDES),
        PROJECT.rglob('gamefixes-*/*.py'),
    )
    py_bin = which('python')

    if not py_bin:
        sys.exit(1)

    # Expect this operation to fail
    for future in await gather(*[run_subproc(py_bin, file) for file in files]):
        ret, file = future
        if ret != 0:
            err = f'The following file has an invalid import: {file}'
            raise RuntimeError(err)


if __name__ == '__main__':
    run_async(main())
