TESTS := ptsched-tests.py
OUTFILES := ptsched ptsched-event-helper
OUTFILES_INSTALL := $(addprefix ~/bin/, $(OUTFILES))
OUTFILES_BUILD := $(addprefix out/bin/, $(OUTFILES))

all: build test

build: $(OUTFILES_BUILD)

deploy: all $(OUTFILES_INSTALL)

test: build ptsched-tests.py
	$(foreach test, $(TESTS), python3 $(test);)

interactive: build
	dev/test

~/bin/%: out/bin/%
	cp $< $@

out/bin/ptsched: ptsched.py
	cp ptsched.py out/bin/ptsched

out/bin/ptsched-event-helper: ptsched-event-helper/ptsched-event-helper/ptsched-event-helper.swift
	xcodebuild -project ptsched-event-helper/ptsched-event-helper.xcodeproj
	cp ptsched-event-helper/build/Release/ptsched-event-helper out/bin/ptsched-event-helper

.PHONY: test
