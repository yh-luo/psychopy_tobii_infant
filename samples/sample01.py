# Calibration
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
# correct path for calibration stimuli
CALISTIMS = [
    'infant/{}'.format(x) for x in os.listdir(os.path.join(DIR, 'infant'))
    if '.png' in x
]

###############################################################################
# Demo
###############################################################################
# create a Window to control the monitor
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
# Open a data file to save gaze data
controller.open_datafile('test_infant_calibration.tsv')

# show the status of eye tracker
controller.show_status("infant/elmo's ducks.mp4")

ret = controller.run_calibration(CALIPOINTS, CALISTIMS, start_key=None)

if ret == 'abort':
    core.quit()

controller.subscribe()
running = True
while running:
    currentGazePosition = controller.get_current_gaze_position()
    if np.nan not in currentGazePosition:
        gaze.setPos(currentGazePosition[0:2])

    keys = event.getKeys()
    for key in keys:
        if key == 'space':
            running = False
            break

    gaze.draw()
    win.flip()

controller.unsubscribe()
controller.close_datafile()

win.close()
core.quit()
