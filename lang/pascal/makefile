main.bin: main.pas pas_parser.pas pas_product.pas
	fpc -Fu../../_output/ -Mdelphiunicode -dconv $^

pas_parser.pas pas_product.pas:
	python ../../view/grm/pparser.py  ../../view/pas/pas.g --code pas_parser.pas
	python ../../view/grm/pproduct.py ../../view/pas/pas.g --code pas_product.pas


clean:
	rm main main.bin *.o *.ppu 