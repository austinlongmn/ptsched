export PTSCHED_DEBUG_CALENDAR := Test Calendar

build: test out/ptsched out/ptsched-event-helper

deploy: build ~/.local/bin/ptsched ~/.local/bin/ptsched-event-helper

test: ptsched.py ptsched-tests.py
	./ptsched-tests.py

interactive: build
	dev/test

~/.local/bin/%: out/%
	cp $< $@

out/ptsched: ptsched.py
	cp ptsched.py out/ptsched

out/ptsched-event-helper: event-helper/main.swift
	swiftc -o $@ $<

.PHONY: test
