#!/usr/bin/env bash

#
# Lint with Pylint
#

# Lint the following gamefix dir: 
# steam, gog, amazon, egs, humble, itchio, ubisoft, umu, zoomplatform
mapfile -d '' files_array < <(find ./{,gamefixes-steam,gamefixes-amazon,gamefixes-gog,gamefixes-egs,gamefixes-humble,gamefixes-itchio,gamefixes-ubisoft,gamefixes-umu,gamefixes-zoomplatform} -type f -name "*.py" ! -name "__init__.py" -print0)

# Disable these checks:
# - E0401: Import errors because umu-protonfixes will be renamed at release
# - C0103: Invalid identifier names for files, as gamefixes are numeric
# - C0116: Missing docstrings for functions or method
# - C0301: Long lines
pylint --rcfile pyproject.toml --disable E0401,C0103,C0116,C0301 "${files_array[@]}"
