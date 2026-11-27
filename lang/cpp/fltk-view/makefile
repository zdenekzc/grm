
FLTK_CONFIG = fltk-config 
FLTK_CFLAGS = $(shell $(FLTK_CONFIG) --cflags )
FLTK_LDFLAGS = $(shell $(FLTK_CONFIG) --ldflags )

CXXFLAGS += $(FLTK_CFLAGS)
LDFLAGS  += $(FLTK_LDFLAGS)

fltk-view.bin: fltk-view.cc
	$(CXX) -o $@ $^ $(LDFLAGS)

clean:
	@rm -f  fltk-view.bin *.o

# dnf install fltk-devel
