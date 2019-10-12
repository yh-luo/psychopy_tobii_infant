#!/usr/bin/env python
import numpy as np
import os

from psychopy import visual, event, core, prefs
prefs.general['audioLib'] = ['sounddevice']

from psychopy_tobii_infant import tobii_controller

###############################################################################
# Constants
DIR = os.path.dirname(__file__)
# users should know the display well.
DISPSIZE = (1280, 1024)
# define calibration points
CALINORMP = [(-0.4, 0.4), (-0.4, -0.4), (0.0, 0.0), (0.4, 0.4), (0.4, -0.4)]
CALIPOINTS = [(x * DISPSIZE[0], y * DISPSIZE[1]) for x, y in CALINORMP]

###############################################################################
# Demo
# create a Window to control the monitor
win = visual.Window(
    size=[1280, 1024],
    units='pix',
    fullscr=True,
    allowGUI=False)

# initialize tobii_controller to communicate with the eyetracker
controller = tobii_controller(win)

controller.show_position()

core.quit()
