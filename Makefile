build: test out/ptsched out/ptsched-event-helper

deploy: test ~/bin/ptsched ~/bin/ptsched-event-helper

test: ptsched.py ptsched-tests.py
	./ptsched-tests.py

interactive: build test
	dev/test

~/bin/%: out/%
	cp $< $@

out/ptsched: ptsched.py
	cp ptsched.py out/ptsched

out/ptsched-event-helper: event-helper.applescript
	@echo "#!/usr/bin/env osascript" > out/ptsched-event-helper
	osacompile -o /dev/stdout event-helper.applescript >> out/ptsched-event-helper
	@chmod u+x out/ptsched-event-helper

.PHONY: test
