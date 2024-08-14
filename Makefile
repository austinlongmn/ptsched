build: out/ptsched out/ptsched-tools

deploy: ~/bin/ptsched ~/bin/ptsched-tools

~/bin/ptsched: out/ptsched
	cp ptsched ~/bin/ptsched

out/ptsched: ptsched
	cp ptsched out/ptsched

~/bin/ptsched-tools: out/ptsched-tools
	cp ptsched-tools ~/bin/ptsched-tools

out/ptsched-tools: ptsched-tools
	cp ptsched-tools out/ptsched-tools
