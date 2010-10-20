#!/usr/bin/env python
#######################################
#
# some always needed helpers
#
# author:(c) Michael Aschauer <m AT ash.to>
# www: http:/m.ash.to
# licenced under: GPL v3
# see: http://www.gnu.org/licenses/gpl.html
#
#######################################

import os

def checkPath(path):
	if os.path.isdir(path):
		return True
	else:
		if not os.path.isdir(os.path.dirname(path)) and not os.path.dirname(path) == "":
			checkPath(os.path.dirname(path))
		os.mkdir(path)

def createPath(file):
	checkPath(os.path.dirname(file))
