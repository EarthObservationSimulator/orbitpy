# Project:        TAT-C
# Created by:     Joey Gurganus
# Date:           2019.02.28


# Define macros for locations
SUBS = oc rm  

all install clean bare runtest:
	-X=`pwd`; \
	for i in $(SUBS); \
	do echo '<<<' $$i '>>>'; cd $$X/$$i; make $@; done
