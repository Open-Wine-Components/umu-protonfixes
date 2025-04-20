#!/usr/bin/env sh

export DEB_BUILD_MAINT_OPTIONS=hardening=-format
export PYBUILD_NAME=xlib
make
