export DEVELOPER_DIR := /Applications/Xcode.app
export PTSCHED_DEBUG_CALENDAR := Test Calendar

build: test out/ptsched out/ptsched-event-helper

deploy: build ~/bin/ptsched ~/bin/ptsched-event-helper

test: ptsched.py ptsched-tests.py
	./ptsched-tests.py

interactive: build
	dev/test

~/bin/%: out/%
	cp $< $@

out/ptsched: ptsched.py
	cp ptsched.py out/ptsched

out/ptsched-event-helper: ptsched-event-helper/ptsched-event-helper/main.swift
	xcodebuild -project ptsched-event-helper/ptsched-event-helper.xcodeproj
	cp ptsched-event-helper/build/Release/ptsched-event-helper out/ptsched-event-helper

.PHONY: test
