import os
import numpy as np
from psychopy import core, visual, event

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
# To get the results in pixel, the monitor needs to be defined beforehead.
win = visual.Window(size=[1280, 1024],
                    units='pix',
                    monitor='Tobii',
                    fullscr=True,
                    allowGUI=False)

# initialize tobii_controller to communicate with the eyetracker
controller = tobii_controller(win)

# show the relative position of the subject to the eyetracker
# stimuli in show_status are in 'height' units.
# Press space to exit
controller.show_status()

controller.run_calibration(CALIPOINTS)
controller.run_validation(show_results=True)

marker = visual.Rect(win, width=20, height=20, autoLog=False)

# Start recording.
# filename of the data file could be define in this method or when creating an
# tobii_controller instance
controller.start_recording('demo7-test.tsv')
waitkey = True
timer = core.Clock()

# Press space to leave
while waitkey:
    # Get the latest gaze position data.
    currentGazePosition = controller.get_current_gaze_position()

    # The value is numpy.nan if Tobii failed to detect gaze position.
    if np.nan not in currentGazePosition:
        marker.setPos(currentGazePosition)
        marker.setLineColor('white')
    else:
        marker.setLineColor('red')
    keys = event.getKeys()
    if 'space' in keys:
        waitkey = False
    elif len(keys) >= 1:
        # Record the pressed key to the data file.
        controller.record_event(keys[0])
        print('pressed {k} at {t} ms'.format(k=keys[0],
                                             t=timer.getTime() * 1000))

    marker.draw()
    win.flip()

# stop recording
controller.stop_recording()
# close the file
controller.close()

win.close()
core.quit()
