#!/usr/bin/env bash

#
# Lint using Pylint and check for valid symbolic links for directories with fixes.
#

for file in ./{gamefixes-amazon,gamefixes-gog,gamefixes-egs,gamefixes-humble,gamefixes-itchio,gamefixes-ubisoft,gamefixes-ulwgl,gamefixes-zoomplatform}/*; do
    if [[ -L "$file" && ! -e "$file" ]]; then
        echo "The following file is not a valid link: ${file}"
        exit 1
    elif [[ -f "$file" && "$file" != "__init__.py" && ! -L "$file" ]]; then
        # Lint
        # Disable these checks:
        # - Long lines from comments
        # - Import errors because ULWGL-protonfixes will be renamed
        # - Docstrings for functions and modules
        # - Invalid identifier names for files

        pylint --rcfile pyproject.toml --disable C0103,C0116,E0401,C0301,C0114 "$file"
        exit_status=$?
        if [ $exit_status -ne 0 ]; then
            exit 1
        fi
    fi
done
