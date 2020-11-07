#!/usr/bin/env python

from sumolib import checkBinary

import os
import subprocess
import sys

from setenv import set_env

set_env()

sumoBinary = checkBinary('sumo')

retcode = subprocess.call(
    [os.environ.get("SUMO_HOME")+"sumo", "-c", "data/quickstart.sumocfg"], stdout=sys.stdout, stderr=sys.stderr)
print(">> Simulation closed with status %s" % retcode)
sys.stdout.flush()
