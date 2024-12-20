export PTSCHED_DEBUG_CALENDAR := Test Calendar

build: test .venv/bin/ptsched

deploy: build
	pipx install .

test: ptsched/*.py ptsched/bin/event-helper
	.venv/bin/pytest

interactive: build
	dev/test

.venv/bin/ptsched: ptsched/**/* ptsched/bin/event-helper setup.py
	.venv/bin/pip3 install .

ptsched/bin/event-helper: event-helper/main.swift
	swiftc -o $@ $<

.PHONY: test
