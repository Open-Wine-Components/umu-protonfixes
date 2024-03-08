#!/usr/bin/env bash

#
# Lint using Pylint and check for valid symbolic links for directories with fixes.
#

# Links
for file in ./{gamefixes-steam,gamefixes-amazon,gamefixes-gog,gamefixes-egs,gamefixes-humble,gamefixes-itchio,gamefixes-ubisoft,gamefixes-ulwgl,gamefixes-zoomplatform}/*; do
    if [[ -L "$file" && ! -e "$file" ]]; then
        echo "The following file is not a valid link: ${file}"
        exit 1
    fi
done

# Lint
mapfile -d '' files_array < <(find ./{gamefixes-steam,gamefixes-amazon,gamefixes-gog,gamefixes-egs,gamefixes-humble,gamefixes-itchio,gamefixes-ubisoft,gamefixes-ulwgl,gamefixes-zoomplatform} -type f -name "*.py" ! -name "__init__.py" -print0)

# Disable these checks:
# - Long lines from comments
# - Import errors because ULWGL-protonfixes will be renamed at release
# - Docstrings for functions and modules
# - Invalid identifier names for files
pylint --rcfile pyproject.toml --disable C0103,C0116,E0401,C0301,C0114 "${files_array[@]}"
