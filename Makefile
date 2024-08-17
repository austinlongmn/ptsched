build: out/ptsched

deploy: ~/bin/ptsched

test: ptsched.py ptsched-tests.py
	./ptsched-tests.py

~/bin/ptsched: out/ptsched
	cp ptsched ~/bin/ptsched

out/ptsched: ptsched.py
	cp ptsched.py out/ptsched

.PHONY: test
