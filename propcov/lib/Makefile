# Define macros for locations
SUBS = propcov-cpp propcov-cpp/polygon

all install clean bare runtest:
	-X=`pwd`; \
	for i in $(SUBS); \
	do echo '<<<' $$i '>>>'; cd $$X/$$i; make $@; done
