import numpy as np
import os

from psychopy import visual, event, core, prefs
prefs.general['audioLib'] = ['sounddevice']

from psychopy_tobii_infant import tobii_controller

###############################################################################
# Constants
DIR = os.path.dirname(__file__)
# users should know the display well.
DISPSIZE = (34, 27)
# define calibration points
CALINORMP = [(-0.4, 0.4), (-0.4, -0.4), (0.0, 0.0), (0.4, 0.4), (0.4, -0.4)]
CALIPOINTS = [(x * DISPSIZE[0], y * DISPSIZE[1]) for x, y in CALINORMP]

###############################################################################
# Demo
# create a Window to control the monitor
win = visual.Window(
    size=[1280, 1024],
    monitor='tobii', # TODO: change it to the real monitor
    units='cm',
    screen=1,
    fullscr=True,
    allowGUI=False)

gaze = visual.Circle(
    win, size=0.02, lineColor=None, fillColor='white', autoLog=False)

# initialize tobii_controller to communicate with the eyetracker
controller = tobii_controller(win)

# show the relative position of the subject to the eyetracker
# stimuli in show_status are in 'height' units.
# Press space to exit
controller.show_status()

# How to use:
# - Use 1~9 (depending on the number of calibration points) to present
#   calibration stimulus and 0 to hide the target.
# - Press space to start collect calibration samples.
# - Press return (Enter) to finish the calibration and show the result.
# - Choose the points to recalibrate with 1~9.
# - Press decision_key to accept the calibration or recalibrate.
success = controller.run_calibration(CALIPOINTS,start_key=None)
if not success:
    win.close()
    core.quit()

marker = visual.Rect(win, width=1, height=1)

# Start recording.
# filename of the data file could be define in this method or when creating an
# infant_tobii_controller instance
controller.start_recording('demo4-test.tsv')
timer = core.Clock()
waitkey = True
while waitkey:
    # Get the latest gaze position data.
    currentGazePosition = controller.get_current_gaze_position()

    # Gaze position is a tuple: ((left_eye_x, left_eye_y), (right_eye_x, right_eye_y))
    # The value is numpy.nan if Tobii failed to detect gaze position.
    if np.nan not in currentGazePosition[0]:
        marker.setPos(currentGazePosition[0])
        marker.setLineColor('white')
    else:
        marker.setLineColor('red')
    keys = event.getKeys()
    if 'space' in keys:
        waitkey = False
    elif len(keys) >= 1:
        # Record the pressed key to the data file.
        controller.record_event(keys[0])
        print('pressed {k} at {t} ms'.format(
            k=keys[0], t=timer.getTime() * 1000))

    marker.draw()
    win.flip()

# stop recording
controller.stop_recording()
# close the file
controller.close()

win.close()
core.quit()
