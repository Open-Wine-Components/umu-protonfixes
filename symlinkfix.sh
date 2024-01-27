#!/bin/bash
# change symlink targets to lower case if they aren't already
find . -type l | while read symlink; do
  target=$(readlink "$symlink")
  new_target=$(echo "$target" | tr '[:upper:]' '[:lower:]')
  ln -sf "$new_target" "$symlink"
done

# iterate through game folders, check if symlinks are valid, if they are not, remove them

for gamefixes in $(ls | grep gamefixes); do
	cd $gamefixes
	find . -type l | while read symlink; do
  		target=$(readlink "$symlink")
 		if [[ ! -e "$target" ]]; then
			echo "Broken symlink detected, removing: $gamefixes/$(echo "$symlink" | sed 's/^..//')"
    			rm "$symlink"
 		fi
	done
	cd ..
done
