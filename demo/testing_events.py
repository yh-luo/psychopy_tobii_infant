import numpy as np
import os

from psychopy import visual, event, core, prefs
prefs.general['audioLib'] = ['sounddevice']

from psychopy_tobii_infant import infant_tobii_controller

###############################################################################
# Constants
###############################################################################
DIR = os.path.dirname(__file__)
# users should know the display well.
DISPSIZE = (34, 27)
# define calibration points
CALINORMP = [(-0.4, 0.4), (-0.4, -0.4), (0.0, 0.0), (0.4, 0.4), (0.4, -0.4)]
CALIPOINTS = [(x * DISPSIZE[0], y * DISPSIZE[1]) for x, y in CALINORMP]
# stimuli to use in calibration
# The number of stimuli must be the same or larger than the calibration points.
CALISTIMS = [
    'infant/{}'.format(x) for x in os.listdir(os.path.join(DIR, 'infant'))
    if '.png' in x
]

###############################################################################
# Demo
###############################################################################
# create a Window to control the monitor
# It is assumed that the profile of the monitor is know. Thus, stimuli in
# show_status are in 'height' units.
win = visual.Window(
    size=[1280, 1024],
    monitor='tobii',
    units='cm',
    screen=1,
    fullscr=True,
    allowGUI=False)

gaze = visual.Circle(
    win,
    size=0.02,
    lineColor=None,
    fillColor='white',
    autoLog=False)

# initialize tobii_controller to communicate with the eyetracker
controller = infant_tobii_controller(win)

ret = controller.run_calibration(CALIPOINTS, CALISTIMS, start_key=None)

if ret == 'abort':
    core.quit()

marker = visual.Rect(win,width=1,height=1)

# Start recording.
controller.start_recording()
timer = core.Clock()
waitkey = True
while waitkey:
    # Get the latest gaze position data.
    currentGazePosition = controller.get_current_gaze_position()
    
    # Gaze position is a tuple of four values (lx, ly, rx, ry).
    # The value is numpy.nan if Tobii failed to detect gaze position.
    if np.nan not in currentGazePosition[0]:
        marker.setPos(currentGazePosition[0])
        marker.setLineColor('white')
    else:
        marker.setLineColor('red')
    keys = event.getKeys()
    if 'space' in keys:
        waitkey=False
    elif len(keys)>=1:
        # Record the first key name to the data file.
        controller.record_event(keys[0])
        print('pressed {k} at {t}'.format(k=keys[0], t=timer.getTime()-1))

    marker.draw()
    win.flip()

# stop recording
controller.stop_recording()
# close the file
controller.close_datafile()

win.close()
core.quit()
