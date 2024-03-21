#!/usr/bin/env bash

#
# Check for valid symbolic links for non-Steam gamefixes
#

# Lint the following gamefix dir: 
# gog, amazon, egs, humble, itchio, ubisoft, umu, zoomplatform
for file in ./{gamefixes-amazon,gamefixes-gog,gamefixes-egs,gamefixes-humble,gamefixes-itchio,gamefixes-ubisoft,gamefixes-umu,gamefixes-zoomplatform}/*; do
    if [[ -L "$file" && ! -e "$file" ]]; then
        echo "The following file is not a valid link: ${file}"
        exit 1
    fi
done
