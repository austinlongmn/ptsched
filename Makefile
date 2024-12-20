export PTSCHED_DEBUG_CALENDAR := Test Calendar
export PATH := .venv/bin:$(PATH)

build: test .venv/bin/ptsched

deploy: build ~/.local/bin/ptsched ~/.local/bin/ptsched-event-helper

test: ptsched/*.py ptsched/bin/event-helper
	pytest

interactive: build
	dev/test

.venv/bin/ptsched: ptsched/**/* ptsched/bin/event-helper setup.py
	pip3 install .

ptsched/bin/event-helper: event-helper/main.swift
	swiftc -o $@ $<

.PHONY: test
