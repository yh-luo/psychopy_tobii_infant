# Calibration
import numpy as np
import os

from psychopy import visual, event, core, prefs
prefs.general['audioLib'] = ['sounddevice']
from psychopy.constants import FINISHED

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


def _unload(self):
    try:
        # remove textures from graphics card to prevent crash
        self.clearTextures()
    except Exception:
        pass

    if self._mov is not None:
        self._mov.close()
    self._mov = None
    self._numpyFrame = None
    if self._audioStream is not None:
        self._audioStream.stop()
    self._audioStream = None
    self.status = FINISHED


# Currently, there is a bug in MovieStim3 that makes it unable to stop
# playing the video
visual.MovieStim3._unload = _unload

gaze = visual.Circle(
    win,
    size=0.02,
    units='height',
    lineColor=None,
    fillColor='white',
    autoLog=False)

# initialize tobii_controller to communicate with the eyetracker
controller = infant_tobii_controller(win)
# Open a data file to save gaze data
controller.open_datafile('test_infant_calibration.tsv')

# show the status of eye tracker
controller.show_status("infant/elmo's ducks.mp4")

# the calibration points should not be shuffled, considering the stimulus will
# be presented manually!
ret = controller.run_infant_calibration(CALIPOINTS, CALISTIMS, start_key=None)

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
