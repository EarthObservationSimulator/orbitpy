# Created by:     Vinay Ravindra
# Date:           2020.02.11


PROJECT := orbitpy

.DEFAULT_GOAL := all

AUX = propcov
TEST = tests

DOC = docs

.PHONY: aux aux_clean aux_bare docs docs_clean

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  all        to perform clean-up and installation"
	@echo "  install    to set up the python package (pip install -e .)"
	@echo "  runtest    to perform unit testing"
	@echo "  clean      to remove *.pyc files and __pycache__ directories"
	@echo "  bare       to uninstall the package and remove *egg*"

all: bare install docs

aux: aux_bare # install the propcov package
	-X=`pwd`; \
	echo '<<<' $$AUX '>>>'; cd $$X; cd $(AUX); make all;

aux_clean: 
	-X=`pwd`; \
	echo '<<<' $$AUX '>>>'; cd $$X; cd $(AUX); make clean;

aux_bare: 
	-X=`pwd`; \
	echo '<<<' $$AUX '>>>'; cd $$X; cd $(AUX); make bare;

docs: docs_clean #Build the documentation
	-X=`pwd`; \
	echo '<<<' $$DOC '>>>'; cd $$X; cd $(DOC); make html;

docs_clean: 
	-X=`pwd`; \
	echo '<<<' $$DOC '>>>'; cd $$X; cd $(DOC); make clean;

install: aux
	pip install -e .

runtest:
	-X=`pwd`; \
	cd $$X; cd $(TEST); python -m unittest discover

clean: aux_clean docs_clean
	@echo "Cleaning up..."
	@find . -name "*.pyc" -delete
	@find . -type d -name __pycache__ -print0 | xargs -0 rm -rf

bare: clean aux_bare docs_clean
	pip uninstall -y $(PROJECT) 
	rm -rf $(PROJECT).egg-info

