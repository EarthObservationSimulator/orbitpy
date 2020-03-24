# Created by:     Vinay Ravindra
# Date:           2020.02.11


PROJECT := OrbitPy


.DEFAULT_GOAL := all

AUX = oci
AUX_DRIVER = mission
AUX_OBJ = $(AUX_DRIVER).o
AUX_BIN = $(AUX)/bin

.PHONY: aux aux_clean aux_bare

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  all        to perform clean-up and installation"
	@echo "  install    to set up the python package (pip install -e .)"
	@echo "  runtest    to perform unit testing"
	@echo "  testlog    to perform unit testing with no log capture"
	@echo "  fulltest   to perform unit testing with no log capture and with verbose"
	@echo "  clean      to remove *.pyc files and __pycache__ directories"
	@echo "  bare       to uninstall the package and remove *egg*"

all: aux bare install

aux: bare #Build the OC Interface binaries
	-X=`pwd`; \
	do echo '<<<' $$AUX '>>>'; cd $$X; cd $(AUX); make all; done

aux_clean: 
	-X=`pwd`; \
	do echo '<<<' $$AUX '>>>'; cd $$X; cd $(AUX); make clean; done

aux_bare: 
	-X=`pwd`; \
	do echo '<<<' $$AUX '>>>'; cd $$X; cd $(AUX); make bare; done

install: aux
	pip install -e .

runtest:
	@nosetests --exe

testlog:
	@nosetests --nologcapture --exe

fulltest:
	@nosetests --nologcapture -v --exe

clean: aux_clean
	@echo "Cleaning up..."
	@find . -name "*.pyc" -delete
	@find . -type d -name __pycache__ -print0 | xargs -0 rm -rf


bare: clean aux_bare
	pip uninstall -y $(PROJECT) 
	rm -rf $(PROJECT).egg-info .eggs