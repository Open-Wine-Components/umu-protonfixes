OBJDIR  := builddir

PREFIX  ?= /usr
DESTDIR := $(shell pwd)/dist/protonfixes

.PHONY: all

all: xrandr-dist

.PHONY: install

install: protonfixes-install xrandr-install

#
# protonfixes
#

.PHONY: protonfixes

protonfixes-install: protonfixes
	$(info :: Installing protonfixes )
	install -d              $(DESTDIR)
	cp      -r gamefixes-*  $(DESTDIR)
	cp      -r verbs        $(DESTDIR)
	cp         *.py         $(DESTDIR)
	cp         winetricks   $(DESTDIR)
	rm $(DESTDIR)/protonfixes_test.py

#
# xrandr
#

$(OBJDIR)/.build-xrandr-dist: | $(OBJDIR)
	$(info :: Building xrandr )
	cd subprojects/x11-xserver-utils/xrandr && \
	./configure --prefix=/usr && \
	make
	touch $(@)

.PHONY: xrandr-dist

xrandr-dist: $(OBJDIR)/.build-xrandr-dist

xrandr-install: xrandr-dist
	$(info :: Installing xrandr )
	cp subprojects/x11-xserver-utils/xrandr/xrandr $(DESTDIR)

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
	make DESTDIR=$(DESTDIR) install
	cp $(DESTDIR)/usr/bin/cabextract $(DESTDIR)
	rm -r $(DESTDIR)/usr
$(OBJDIR):
	@mkdir -p $(@)
