
SHELL := /bin/bash

BUILD ?= build
DIST  ?= dist

OBJDIR := $(shell realpath $(BUILD))
DSTDIR := $(shell realpath $(DIST))
TARGET_DIR := $(DSTDIR)

BASEDIR       := /files

# Default flags are from Proton, CFLAGS/LDFLAGS are expected to tbe overriden by Proton's makefile
TARGET_ARCH ?= x86_64

ifeq ($(TARGET_ARCH),arm64)
	TARGET_ARCH_unix := aarch64
	CFLAGS ?= -march=armv8.2-a -mtune=cortex-x3
else
	TARGET_ARCH_unix := x86_64
	CFLAGS ?= -O2 -march=nocona -mtune=core-avx2
endif

LDFLAGS ?= -Wl,-O1,--sort-common,--as-needed
LIBDIR := $(BASEDIR)/lib/$(TARGET_ARCH_unix)-linux-gnu

.PHONY: all

all: winetricks-dist cabextract-dist libmspack-dist unzip-dist procps-ng-dist

.PHONY: install

# Note: `export DEB_BUILD_MAINT_OPTIONS=hardening=-format` is required for the unzip target
install: protonfixes-install winetricks-install cabextract-install libmspack-install unzip-install procps-ng-install

TARGET_STEAMRT := $(shell source /etc/os-release && echo -n $$VERSION_CODENAME)

ifeq ($(TARGET_STEAMRT),steamrt4)
all: zenity-rs-dist
install: zenity-rs-install
endif

#
# protonfixes
#

.PHONY: protonfixes

protonfixes-install: protonfixes
	$(info :: Installing protonfixes )
	install -d              $(TARGET_DIR)
	cp      -r gamefixes-*  $(TARGET_DIR)
	cp      -r verbs        $(TARGET_DIR)
	cp         *.py         $(TARGET_DIR)
	mkdir   -p              $(TARGET_DIR)$(BASEDIR)/bin
	cp         umu-database.csv   $(TARGET_DIR)
	rm $(TARGET_DIR)/protonfixes_test.py

#
# winetricks
#

$(OBJDIR)/winetricks: | $(OBJDIR)
	rsync -arx --delete subprojects/winetricks $(OBJDIR)


$(OBJDIR)/.build-winetricks-dist: | $(OBJDIR)/winetricks
	$(info :: Building winetricks )
	find $(CURDIR)/patches/winetricks/ -name "*.patch" | sort | xargs -n1 patch -d $(OBJDIR)/winetricks -Np1 -i
	touch $(@)

.PHONY: winetricks-dist winetricks-install

winetricks-dist: $(OBJDIR)/.build-winetricks-dist

winetricks-install: winetricks-dist
	install -d $(TARGET_DIR)$(BASEDIR)/bin
	install -m755 $(OBJDIR)/winetricks/src/winetricks $(TARGET_DIR)$(BASEDIR)/bin/winetricks

	install -d $(TARGET_DIR)
	install -m755 $(OBJDIR)/winetricks/src/winetricks $(TARGET_DIR)/winetricks

#
# libmspack and cabextract
#

$(OBJDIR)/libmspack: | $(OBJDIR)
	rsync -arx --delete subprojects/libmspack $(OBJDIR)

#
# cabextract
#

$(OBJDIR)/.build-cabextract-dist: | $(OBJDIR)/libmspack
	$(info :: Building cabextract )
	cd $(OBJDIR)/libmspack/cabextract && \
	autoreconf -fiv -I /usr/share/gettext/m4/ && \
	./configure --prefix=$(BASEDIR) --libdir=$(LIBDIR) && \
	make
	touch $(@)

.PHONY: cabextract-dist

cabextract-dist: $(OBJDIR)/.build-cabextract-dist

cabextract-install: cabextract-dist
	$(info :: Installing cabextract )
	cd $(OBJDIR)/libmspack/cabextract && \
	make DESTDIR=$(TARGET_DIR) install
	rm -r $(TARGET_DIR)$(BASEDIR)/share

#
# libmspack
#

$(OBJDIR)/.build-libmspack-dist: | $(OBJDIR)/libmspack
	$(info :: Building libmspack )
	cd $(OBJDIR)/libmspack/libmspack && \
	autoreconf -vfi && \
	./configure --prefix=$(BASEDIR) --libdir=$(LIBDIR) --disable-static && \
	sed -i -e 's/ -shared / -Wl,-O1,--as-needed\0/g' libtool && \
	make
	touch $(@)

.PHONY: libmspack-dist

libmspack-dist: $(OBJDIR)/.build-libmspack-dist

libmspack-install: libmspack-dist
	$(info :: Installing libmspack )
	cd $(OBJDIR)/libmspack/libmspack && \
	make DESTDIR=$(TARGET_DIR) install
	rm -r $(TARGET_DIR)$(BASEDIR)/include
	rm -r $(TARGET_DIR)$(LIBDIR)/pkgconfig
	rm    $(TARGET_DIR)$(LIBDIR)/libmspack.la

#
# unzip
#

DEFINES = -DACORN_FTYPE_NFS -DWILD_STOP_AT_DIR -DLARGE_FILE_SUPPORT \
 -DUNICODE_SUPPORT -DUNICODE_WCHAR -DUTF8_MAYBE_NATIVE -DNO_LCHMOD \
 -DDATE_FORMAT=DF_YMD -DUSE_BZIP2 -DIZ_HAVE_UXUIDGID -DNOMEMCPY \
 -DNO_WORKING_ISPRINT
UNZIP_VERSION := 6.0
UNZIP_DEBIAN_REVISION := 29
UNZIP_BASE_URL := https://deb.debian.org/debian/pool/main/u/unzip
UNZIP_ORIG_TARBALL := unzip_$(UNZIP_VERSION).orig.tar.gz
UNZIP_DEBIAN_TARBALL := unzip_$(UNZIP_VERSION)-$(UNZIP_DEBIAN_REVISION).debian.tar.xz
UNZIP_DOWNLOAD_DIR := $(OBJDIR)/downloads/unzip

$(UNZIP_DOWNLOAD_DIR):
	mkdir -p $(@)

$(UNZIP_DOWNLOAD_DIR)/$(UNZIP_ORIG_TARBALL): | $(UNZIP_DOWNLOAD_DIR)
	$(info :: Downloading $(UNZIP_ORIG_TARBALL) )
	python3 -c 'from urllib.request import urlretrieve; urlretrieve("$(UNZIP_BASE_URL)/$(UNZIP_ORIG_TARBALL)", "$@")'

$(UNZIP_DOWNLOAD_DIR)/$(UNZIP_DEBIAN_TARBALL): | $(UNZIP_DOWNLOAD_DIR)
	$(info :: Downloading $(UNZIP_DEBIAN_TARBALL) )
	python3 -c 'from urllib.request import urlretrieve; urlretrieve("$(UNZIP_BASE_URL)/$(UNZIP_DEBIAN_TARBALL)", "$@")'

$(OBJDIR)/unzip: $(UNZIP_DOWNLOAD_DIR)/$(UNZIP_ORIG_TARBALL) $(UNZIP_DOWNLOAD_DIR)/$(UNZIP_DEBIAN_TARBALL)
	rm -rf $(@)
	mkdir -p $(@)
	tar -xzf $(UNZIP_DOWNLOAD_DIR)/$(UNZIP_ORIG_TARBALL) -C $(@) --strip-components=1
	tar -xJf $(UNZIP_DOWNLOAD_DIR)/$(UNZIP_DEBIAN_TARBALL) -C $(@)

$(OBJDIR)/.build-unzip-dist: $(OBJDIR)/unzip
	$(info :: Building unzip )
	cd $(OBJDIR)/unzip && \
	while read -r pch; do patch -Np1 -i debian/patches/$$pch || exit 1; done < debian/patches/series && \
	make -f unix/Makefile prefix=$(BASEDIR) D_USE_BZ2=-DUSE_BZIP2 L_BZ2=-lbz2 LF2="$(LDFLAGS)" CF="$(CFLAGS) -I. $(DEFINES)" unzips
	touch $(@)

.PHONY: unzip-dist

unzip-dist: $(OBJDIR)/.build-unzip-dist

unzip-install: unzip-dist
	$(info :: Installing unzip )
	cd $(OBJDIR)/unzip && \
	make -f unix/Makefile prefix=$(TARGET_DIR)$(BASEDIR) install
	# Post install
	rm -r $(TARGET_DIR)$(BASEDIR)/man

#
# procps-ng
#

$(OBJDIR)/procps-ng: | $(OBJDIR)
	rsync -arx --delete subprojects/procps-ng $(OBJDIR)

$(OBJDIR)/.build-procps-ng-dist: | $(OBJDIR)/procps-ng
	$(info :: Building procps-ng )
	cd $(OBJDIR)/procps-ng && \
	./autogen.sh && \
	./configure --prefix=$(BASEDIR) --libdir=$(LIBDIR) --disable-static --disable-nls --without-ncurses && \
	make
	touch $(@)

.PHONY: procps-ng-dist

procps-ng-dist: $(OBJDIR)/.build-procps-ng-dist

procps-ng-install: procps-ng-dist
	$(info :: Installing procps-ng )
	install -d $(TARGET_DIR)$(BASEDIR)/bin
	install -m755 $(OBJDIR)/procps-ng/src/pgrep $(TARGET_DIR)$(BASEDIR)/bin/pgrep
	install -m755 $(OBJDIR)/procps-ng/src/pkill $(TARGET_DIR)$(BASEDIR)/bin/pkill
	install -d $(TARGET_DIR)$(LIBDIR)
	install -m755 $(OBJDIR)/procps-ng/library/.libs/libproc2.so.* $(TARGET_DIR)$(LIBDIR)/

#
# zenity-rs
#

ZENITY_RS_VER := 0.2.8
ZENITY_RS_x86_64_SHA256 := 797bd492a8723d741d888320ab87b934b0c4571a1ff2c128963a08daa35df8c7
ZENITY_RS_aarch64_SHA256 := c3f8a11fdc17632ffe3d5b1640a931139c2b8d86145c531e0f4db8a63ca3f2a2

$(OBJDIR)/zenity-rs: | $(OBJDIR)
	mkdir -p $(@)

$(OBJDIR)/.build-zenity-rs-dist: | $(OBJDIR)/zenity-rs
	$(info :: Downloading zenity-rs )
	cd $(OBJDIR)/zenity-rs && \
	curl -L "https://github.com/QaidVoid/zenity-rs/releases/download/v$(ZENITY_RS_VER)/zenity-rs-$(TARGET_ARCH_unix)-linux" --output zenity-rs
	touch $(@)

.PHONY: zenity-rs-dist

zenity-rs-dist: $(OBJDIR)/.build-zenity-rs-dist

zenity-rs-install: zenity-rs-dist
	$(info :: Installing zenity-rs )
	install -d $(TARGET_DIR)$(BASEDIR)/bin
	install -m755 $(OBJDIR)/zenity-rs/zenity-rs $(TARGET_DIR)$(BASEDIR)/bin/zenity


$(OBJDIR):
	@mkdir -p $(@)
