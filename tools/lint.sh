#!/usr/bin/env bash

#
# Lint with Pylint
#

# Lint the following gamefix dir: 
# steam, gog, amazon, egs, humble, itchio, ubisoft, umu, zoomplatform
mapfile -d '' files_array < <(find ./{gamefixes-steam,gamefixes-amazon,gamefixes-gog,gamefixes-egs,gamefixes-humble,gamefixes-itchio,gamefixes-ubisoft,gamefixes-umu,gamefixes-zoomplatform} -type f -name "*.py" ! -name "__init__.py" -print0)

# Disable these checks:
# - Long lines from comments
# - Import errors because umu-protonfixes will be renamed at release
# - Docstrings for functions and modules
# - Invalid identifier names for files
pylint --rcfile pyproject.toml --disable C0103,C0116,E0401,C0301,C0114 "${files_array[@]}"
