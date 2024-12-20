export PTSCHED_DEBUG_CALENDAR := Test Calendar

build: out/ptsched out/ptsched-event-helper

deploy: build ~/.local/bin/ptsched ~/.local/bin/ptsched-event-helper

test: ptsched/* tests/ptsched_tests.py
	python3 tests/ptsched_tests.py

interactive: build
	dev/test

~/.local/bin/%: out/%
	cp $< $@

out/ptsched: ptsched/*
	python3 -m zipapp ptsched -o out/ptsched -p "/usr/bin/env python3"

out/ptsched-event-helper: event-helper/main.swift
	swiftc -o $@ $<

.PHONY: test
