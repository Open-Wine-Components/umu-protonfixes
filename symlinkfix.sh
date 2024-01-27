#!/bin/bash
# change symlink targets to lower case if they aren't already
find . -type l | while read symlink; do
  target=$(readlink "$symlink")
  new_target=$(echo "$target" | tr '[:upper:]' '[:lower:]')
  ln -sf "$new_target" "$symlink"
done
