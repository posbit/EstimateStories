PREFIX=/usr
PREFIX_BIN=$(PREFIX)/bin

.PHONY: install

install:
	mkdir -p $(PREFIX_BIN)
	cp ./estimate-stories.py $(PREFIX_BIN)/estimate-stories
