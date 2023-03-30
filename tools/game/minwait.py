#!/usr/bin/env python
# -*- coding: utf8 -*-
# Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.org/sumo
# Copyright (C) 2010-2023 German Aerospace Center (DLR) and others.
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# https://www.eclipse.org/legal/epl-2.0/
# This Source Code may also be made available under the following Secondary
# Licenses when the conditions for such availability set forth in the Eclipse
# Public License 2.0 are satisfied: GNU General Public License, version 2
# or later which is available at
# https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html
# SPDX-License-Identifier: EPL-2.0 OR GPL-2.0-or-later

# @file    minwait.py
# @author  Michael Behrisch
# @date    2023-03-29

"""
This script runs the gaming GUI for the LNdW traffic light game.
It checks for possible scenarios in the current working directory
and lets the user start them as a game. Furthermore it
saves highscores to local disc and to the central highscore server.
"""
from __future__ import absolute_import
from __future__ import print_function
import os
import subprocess
import sys
import glob
import pickle

from runner import computeScoreFromWaitingTime, _SCOREFILE

SUMO_HOME = os.environ.get('SUMO_HOME',
                           os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.append(os.path.join(SUMO_HOME, 'tools'))
import sumolib  # noqa


base = os.path.dirname(sys.argv[0])
high = {}
for config in sorted(glob.glob(os.path.join(base, "*.sumocfg"))):
    tls = None
    for a in sumolib.xml.parse_fast(config, "additional-files", "value"):
        for f in a.value.split(","):
            if ".tll" in f or ".tls" in f:
                tls = f
                break
    if tls:
        with open(tls) as tls_in, open(tls + ".act", "w") as tls_out:
            for line in tls_in:
                line = line.replace('type="static"', 'type="actuated"')
                if "phase" in line:
                    line = line.replace('duration="10000"', 'duration="10" minDur="0" maxDur="10000"')
                tls_out.write(line)
        scen = os.path.basename(config)[:-8]
        subprocess.call([sumolib.checkBinary("sumo"), "-c", config, "-a", a.value.replace(tls, tls + ".act"),
                         '--duration-log.statistics', '--statistic-output', scen + '.stats.xml',
                         '--tripinfo-output.write-unfinished'])
        score = computeScoreFromWaitingTime(scen)
        high[scen] = [("actuated", "", score[0])]
print(high)
with open(_SCOREFILE, 'wb') as pkl:
    pickle.dump(high, pkl)