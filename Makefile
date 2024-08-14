all: ~/bin/ptsched ~/bin/ptsched-tools

~/bin/ptsched: ptsched
	cp ptsched ~/bin/ptsched

~/bin/ptsched-tools: ptsched-tools
	cp ptsched-tools ~/bin/ptsched-tools
