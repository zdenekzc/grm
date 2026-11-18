# Makefile for ToaruOS example programs.
#
# Build requires the ToaruOS cross-toolchain. Easiest is to use the
# prepared container image toaruos/build-tools and call make through
# setup-toaruos.sh (./setup-toaruos.sh --install).
#
# Add new programs by appending source files and binary names below.

CC = x86_64-pc-toaru-gcc

TOARU_ROOT ?= $(CURDIR)/toaruos

CFLAGS  = -O2 -Wall --sysroot=$(TOARU_ROOT)/base \
          -I$(TOARU_ROOT)/base/usr/include
LDFLAGS = --sysroot=$(TOARU_ROOT)/base -L$(TOARU_ROOT)/base/lib

# Yutani GUI libraries — covers decorations + menu + text + icon_cache +
# markup and their transitive dependencies (see toaruos/util/auto-dep.krk).
GUI_LIBS = -ltoaru_decorations -ltoaru_menu -ltoaru_text \
           -ltoaru_icon_cache  -ltoaru_markup \
           -ltoaru_yutani -ltoaru_graphics -ltoaru_kbd \
           -ltoaru_hashmap -ltoaru_list -ltoaru_pex

GUI_PROGS = tree

all: $(GUI_PROGS)

$(GUI_PROGS): %: %.c toaru_compat.h
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS) $(GUI_LIBS)

clean:
	rm -f $(GUI_PROGS)

.PHONY: all clean
