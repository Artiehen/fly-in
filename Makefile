PYTHON = python3
CONFIG = maps.txt
FLAKE8 = flake8
MYPY = mypy
PDB = pdb
MAIN = main.py
CACHE = __pycache__
MYPYCACHE = .mypy_cache
SOURCE = source

all: run

install:
	pip install $(MYPY)
	pip install $(FLAKE8)
	pip install $(INSTALL_MAZEGEN)

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m $(PDB) $(MAIN) $(CONFIG)

lint:
	$(PYTHON) -m $(FLAKE8)
	$(PYTHON) -m $(MYPY) . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

clean:
	rm -rf $(VENV) $(CACHE) $(MYPYCACHE)

re: clean all

.PHONY: all install vrt run debug build lint clean re