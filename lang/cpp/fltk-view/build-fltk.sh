test -d _library || mkdir _library
cd _library || exit 1

# test -f fluid.tar.gz || wget https://www.muquit.com/muquit/software/fluid_hack/fluid.tar.gz

# test -d Fl_Highlight_Editor || git clone  https://github.com/sanel/Fl_Highlight_Editor

test -d fltk || git clone https://github.com/fltk/fltk
cd fltk || exit 1

# test -d fluid.orig || mv fluid fluid.orig && tar xzf ../fluid.tar.gz

test -d build || mkdir build
cd build || exit 1

cmake ..
make -j

cd ..

# fltk/build/bin/test/editor
