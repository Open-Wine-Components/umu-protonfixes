OBJDIR  := builddir

PREFIX      ?= /usr
DESTDIR     ?=
INSTALL_DIR ?= $(shell pwd)/dist/protonfixes

.PHONY: all

all: xrandr-dist cabextract-dist libmspack-dist unzip-dist

.PHONY: install

install: protonfixes-install xrandr-install cabextract-install libmspack-install unzip-install

#
# protonfixes
#

.PHONY: protonfixes

protonfixes-install: protonfixes
	$(info :: Installing protonfixes )
	install -d              $(INSTALL_DIR)
	cp      -r gamefixes-*  $(INSTALL_DIR)
	cp      -r verbs        $(INSTALL_DIR)
	cp         *.py         $(INSTALL_DIR)
	cp         winetricks   $(INSTALL_DIR)
	cp         umu-database.csv   $(INSTALL_DIR)
	rm $(INSTALL_DIR)/protonfixes_test.py

#
# xrandr
#

$(OBJDIR)/.build-xrandr-dist: | $(OBJDIR)
	$(info :: Installing xorg-macros )
	cd subprojects/xutils-dev/util-macros && \
	autoreconf -iv && \
	./configure --prefix=/usr && \
	make DESTDIR=$(INSTALL_DIR) install
	$(info :: Building xrandr )
	cd subprojects/x11-xserver-utils/xrandr && \
	autoreconf -iv -I$(INSTALL_DIR)/usr/share/aclocal && \
	./configure --prefix=/usr && \
	make
	touch $(@)

.PHONY: xrandr-dist

xrandr-dist: $(OBJDIR)/.build-xrandr-dist

xrandr-install: xrandr-dist
	$(info :: Installing xrandr )
	# Install
	cd subprojects/x11-xserver-utils/xrandr && \
	make DESTDIR=$(INSTALL_DIR) install
	# Post install
	cp $(INSTALL_DIR)/usr/bin/xrandr $(INSTALL_DIR)
	rm -r $(INSTALL_DIR)/usr

#
# cabextract
#

$(OBJDIR)/.build-cabextract-dist: | $(OBJDIR)
	$(info :: Building cabextract )
	cd subprojects/libmspack/cabextract && \
	./autogen.sh && \
	./configure --prefix=/usr --sysconfdir=/etc --mandir=/usr/share/man && \
	make
	touch $(@)

.PHONY: cabextract-dist

cabextract-dist: $(OBJDIR)/.build-cabextract-dist

cabextract-install: cabextract-dist
	$(info :: Installing cabextract )
	cd subprojects/libmspack/cabextract && \
	make DESTDIR=$(INSTALL_DIR) install
	cp $(INSTALL_DIR)/usr/bin/cabextract $(INSTALL_DIR)
	rm -r $(INSTALL_DIR)/usr

#
# libmspack
#

$(OBJDIR)/.build-libmspack-dist: | $(OBJDIR)
	$(info :: Building libmspack )
	cd subprojects/libmspack/libmspack && \
	autoreconf -vfi && \
	./configure --prefix=/usr --disable-static --sysconfdir=/etc --localstatedir=/var && \
	sed -i -e 's/ -shared / -Wl,-O1,--as-needed\0/g' libtool && \
	make
	touch $(@)

.PHONY: libmspack-dist

libmspack-dist: $(OBJDIR)/.build-libmspack-dist

libmspack-install: libmspack-dist
	$(info :: Installing libmspack )
	cd subprojects/libmspack/libmspack && \
	make DESTDIR=$(INSTALL_DIR) install
	cp -d $(INSTALL_DIR)/usr/lib/libmspack* $(INSTALL_DIR)
	rm -r $(INSTALL_DIR)/usr
	rm    $(INSTALL_DIR)/libmspack.la

#
# unzip
#

DEB_HOST_GNU_TYPE := $(shell dpkg-architecture -qDEB_HOST_GNU_TYPE)
CC = $(DEB_HOST_GNU_TYPE)-gcc
CFLAGS := $(shell dpkg-buildflags --get CFLAGS)
LDFLAGS := $(shell dpkg-buildflags --get LDFLAGS)
CPPFLAGS := $(shell dpkg-buildflags --get CPPFLAGS)
DEFINES = -DACORN_FTYPE_NFS -DWILD_STOP_AT_DIR -DLARGE_FILE_SUPPORT \
 -DUNICODE_SUPPORT -DUNICODE_WCHAR -DUTF8_MAYBE_NATIVE -DNO_LCHMOD \
 -DDATE_FORMAT=DF_YMD -DUSE_BZIP2 -DIZ_HAVE_UXUIDGID -DNOMEMCPY \
 -DNO_WORKING_ISPRINT

$(OBJDIR)/.build-unzip-dist: | $(OBJDIR)
	$(info :: Building unzip )
	cd subprojects/unzip && \
	dpkg-source --before-build . && \
	make -f unix/Makefile prefix=/usr D_USE_BZ2=-DUSE_BZIP2 L_BZ2=-lbz2 CC="$(CC) -Wall" LF2="$(LDFLAGS)" CF="$(CFLAGS) $(CPPFLAGS) -I. $(DEFINES)" unzips
	touch $(@)

.PHONY: unzip-dist

unzip-dist: $(OBJDIR)/.build-unzip-dist

unzip-install: unzip-dist
	$(info :: Installing unzip )
	cd subprojects/unzip && \
	make -f unix/Makefile prefix=$(INSTALL_DIR) install
	# Post install
	cp -a $(INSTALL_DIR)/bin/unzip $(INSTALL_DIR)
	rm -r $(INSTALL_DIR)/bin $(INSTALL_DIR)/man

$(OBJDIR):
	@mkdir -p $(@)
