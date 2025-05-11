OBJDIR      := builddir
PREFIX      ?= /files
LIBDIR       = $(PREFIX)/lib/x86_64-linux-gnu
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
	mkdir   -p              $(INSTALL_DIR)/files/bin
	cp         winetricks   $(INSTALL_DIR)/files/bin
	cp         umu-database.csv   $(INSTALL_DIR)
	rm $(INSTALL_DIR)/protonfixes_test.py

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
	./configure --prefix=$(PREFIX) --libdir=$(LIBDIR) && \
	make
	touch $(@)

.PHONY: cabextract-dist

cabextract-dist: $(OBJDIR)/.build-cabextract-dist

cabextract-install: cabextract-dist
	$(info :: Installing cabextract )
	cd $(OBJDIR)/libmspack/cabextract && \
	make DESTDIR=$(INSTALL_DIR) install
	rm -r $(INSTALL_DIR)/files/share

#
# libmspack
#

$(OBJDIR)/.build-libmspack-dist: | $(OBJDIR)/libmspack
	$(info :: Building libmspack )
	cd $(OBJDIR)/libmspack/libmspack && \
	autoreconf -vfi && \
	./configure --prefix=/files --libdir=/files/lib/x86_64-linux-gnu --disable-static && \
	sed -i -e 's/ -shared / -Wl,-O1,--as-needed\0/g' libtool && \
	make
	touch $(@)

.PHONY: libmspack-dist

libmspack-dist: $(OBJDIR)/.build-libmspack-dist

libmspack-install: libmspack-dist
	$(info :: Installing libmspack )
	cd $(OBJDIR)/libmspack/libmspack && \
	make DESTDIR=$(INSTALL_DIR) install
	rm -r $(INSTALL_DIR)/files/include
	rm -r $(INSTALL_DIR)/files/lib/x86_64-linux-gnu/pkgconfig
	rm    $(INSTALL_DIR)/files/lib/x86_64-linux-gnu/libmspack.la

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
	rsync -arx --delete subprojects/unzip $(OBJDIR)
	cd $(OBJDIR)/unzip && \
	$(foreach pch, $(UNZIP_PATCHES),patch -Np1 -i debian/patches/$(pch) &&) \
	make -f unix/Makefile D_USE_BZ2=-DUSE_BZIP2 L_BZ2=-lbz2 LF2="$(LDFLAGS)" CF="$(CFLAGS) -I. $(DEFINES)" unzips
	touch $(@)

.PHONY: unzip-dist

unzip-dist: $(OBJDIR)/.build-unzip-dist

unzip-install: unzip-dist
	$(info :: Installing unzip )
	cd $(OBJDIR)/unzip && \
	make -f unix/Makefile prefix=$(INSTALL_DIR)/files install
	# Post install
	rm -r $(INSTALL_DIR)/files/man

#
# python-xlib
#

$(OBJDIR)/.build-python-xlib-dist: | $(OBJDIR)
	$(info :: Building python-xlib )
	rsync -arx --delete subprojects/python-xlib $(OBJDIR)
	cd $(OBJDIR)/python-xlib && \
	python setup.py build
	touch $(@)

.PHONY: python-xlib-dist

python-xlib-dist: $(OBJDIR)/.build-python-xlib-dist

python-xlib-install: python-xlib-dist
	$(info :: Installing python-xlib )
	mkdir $(INSTALL_DIR)/_vendor
	cd $(OBJDIR)/python-xlib && mkdir dist && \
	python setup.py install --root=dist --optimize=1 --skip-build && \
	find dist -type d -name Xlib | xargs -I {} mv {} $(INSTALL_DIR)/_vendor; \

$(OBJDIR):
	@mkdir -p $(@)
