# vala-view: malé IDE pro generovaný Vala parser (pas.g)
#
#   make          vygeneruje pas_parser.vala/pas_product.vala a přeloží
#   make run      spustí GUI
#   make clean    smaže binárku, vygenerované .vala a .build/
#
# Potřebuje: valac, gtk+-3.0 (gtksourceview3 už ne).

build: pas_parser.vala pas_product.vala
	@mkdir -p .build
	valac -q --directory .build vala-view.vala ../textio.vala \
	      pas_parser.vala pas_product.vala --pkg gtk+-3.0 \
	      -o $(CURDIR)/vala-view.bin

pas_parser.vala pas_product.vala: ../../pas.g translate.sh
	sh translate.sh

run: build
	./vala-view.bin

clean:
	rm -rf vala-view.bin .build pas_parser.vala pas_product.vala

.PHONY: build run clean
