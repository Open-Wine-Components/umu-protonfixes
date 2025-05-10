OBJDIR  := builddir

PREFIX      ?= /usr
DESTDIR     ?=
INSTALL_DIR ?= $(shell pwd)/dist/protonfixes

.PHONY: all

all: cabextract-dist libmspack-dist unzip-dist python-xlib-dist

.PHONY: install

# Note: `export DEB_BUILD_MAINT_OPTIONS=hardening=-format` is required for the unzip target
install: protonfixes-install cabextract-install libmspack-install unzip-install python-xlib-install

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

# Flags are from Proton
CFLAGS ?= -O2 -march=nocona -mtune=core-avx2
LDFLAGS ?= -Wl,-O1,--sort-common,--as-needed
DEFINES = -DACORN_FTYPE_NFS -DWILD_STOP_AT_DIR -DLARGE_FILE_SUPPORT \
 -DUNICODE_SUPPORT -DUNICODE_WCHAR -DUTF8_MAYBE_NATIVE -DNO_LCHMOD \
 -DDATE_FORMAT=DF_YMD -DUSE_BZIP2 -DIZ_HAVE_UXUIDGID -DNOMEMCPY \
 -DNO_WORKING_ISPRINT
UNZIP_PATCHES := $(shell cat subprojects/unzip/debian/patches/series)

$(OBJDIR)/.build-unzip-dist: | $(OBJDIR)
	$(info :: Building unzip )
	cd subprojects/unzip && \
	$(foreach pch, $(UNZIP_PATCHES),patch -Np1 -i debian/patches/$(pch) &&) \
	make -f unix/Makefile prefix=/usr D_USE_BZ2=-DUSE_BZIP2 L_BZ2=-lbz2 LF2="$(LDFLAGS)" CF="$(CFLAGS) -I. $(DEFINES)" unzips
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

#
# python-xlib
#

$(OBJDIR)/.build-python-xlib-dist: | $(OBJDIR)
	$(info :: Building python-xlib )
	cd subprojects/python-xlib && \
	dpkg-source --before-build . && \
	dh_auto_build -O--buildsystem=pybuild
	touch $(@)

.PHONY: python-xlib-dist

python-xlib-dist: $(OBJDIR)/.build-python-xlib-dist

python-xlib-install: python-xlib-dist
	$(info :: Installing python-xlib )
	mkdir -p $(INSTALL_DIR)/_vendor && \
	cd subprojects/python-xlib && \
	dh_auto_install -O--buildsystem=pybuild && \
	find debian/tmp -type d -name Xlib | xargs -I {} mv {} $(INSTALL_DIR)/_vendor; \

$(OBJDIR):
	@mkdir -p $(@)
