BUILD ?= build
DIST  ?= dist

OBJDIR := $(shell realpath $(BUILD))
DSTDIR := $(shell realpath $(DIST))
TARGET_DIR := $(DSTDIR)

BASEDIR       := /files

TARGET_ARCH ?= x86_64
LIBDIR := $(BASEDIR)/lib/x86_64-linux-gnu
ifeq ($(TARGET_ARCH),arm64)
	LIBDIR := $(BASEDIR)/lib/aarch64-linux-gnu
endif

.PHONY: all

all: cabextract-dist libmspack-dist unzip-dist

.PHONY: install

# Note: `export DEB_BUILD_MAINT_OPTIONS=hardening=-format` is required for the unzip target
install: protonfixes-install cabextract-install libmspack-install unzip-install

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
	cp         winetricks   $(TARGET_DIR)$(BASEDIR)/bin
	cp         winetricks   $(TARGET_DIR)
	cp         umu-database.csv   $(TARGET_DIR)
	rm $(TARGET_DIR)/protonfixes_test.py

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

$(OBJDIR):
	@mkdir -p $(@)
