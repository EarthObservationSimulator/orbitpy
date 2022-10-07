PACKAGE := propcov

all: bare install

install:
	pip install .

clean: 
	@echo "Cleaning up..."
	@find . -name "*.pyc" -delete
	@find . -type d -name __pycache__ -print0 | xargs -0 rm -rf

bare: clean
	pip uninstall -y $(PACKAGE) 
	rm -rf $(PACKAGE).egg-info
	rm -rf build
	find . -name '*.so' -delete # remove any previously created the library file
