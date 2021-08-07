import os

import numpy as np
from psychopy import core, visual

from psychopy_tobii_infant import TobiiInfantController

###############################################################################
# Constants
DIR = os.path.dirname(__file__)
# users should know the display well.
DISPSIZE = (1280, 1024)
# define calibration points
CALINORMP = [(-0.4, 0.4), (-0.4, -0.4), (0.0, 0.0), (0.4, 0.4), (0.4, -0.4)]
CALIPOINTS = [(x * DISPSIZE[0], y * DISPSIZE[1]) for x, y in CALINORMP]
# correct path for calibration stimuli
CALISTIMS = [
    'infant/{}'.format(x) for x in os.listdir(os.path.join(DIR, 'infant'))
    if x.endswith('.png') and not x.startswith('.')
]

###############################################################################
# Demo
# create a Window to control the monitor
win = visual.Window(size=[1280, 1024],
                    units='pix',
                    fullscr=True,
                    allowGUI=False)

# prepare the experiment stimuli
tar_1 = visual.ImageStim(win,
                         'stim/checkboard_big.png',
                         size=[1280, 1024],
                         units='pix',
                         name='big')
tar_2 = visual.ImageStim(win,
                         'stim/checkboard_small.png',
                         size=[1280, 1024],
                         units='pix',
                         name='small')
alltar = [tar_1, tar_2]

# initialize TobiiInfantController to communicate with the eyetracker
controller = TobiiInfantController(win)

# setup the attention grabber during adjusting the participant's position
grabber = visual.MovieStim3(win, "infant/Sea.mp4")
grabber.setAutoDraw(True)
grabber.play()
# show the relative position of the subject to the eyetracker
# Press space to exit
controller.show_status()

# stop the attention grabber
grabber.setAutoDraw(False)
grabber.stop()

# How to use:
# - Use 1~9 (depending on the number of calibration points) to present
#   calibration stimulus and 0 to hide the target.
# - Press space to start collect calibration samples.
# - Press return (Enter) to finish the calibration and show the result.
# - Choose the points to recalibrate with 1~9.
# - Press decision_key (default is space) to accept the calibration or
# recalibrate.
success = controller.run_calibration(CALIPOINTS, CALISTIMS)
if not success:
    core.quit()

# Start recording.
# filename of the data file could be define in this method or when creating an
# TobiiInfantController instance
controller.start_recording('demo2-test.tsv')
# start
np.random.shuffle(alltar)
for target in alltar:
    # Draw the stimuli in each frames
    target.setAutoDraw(True)
    # send an event to the eyetracker
    win.callOnFlip(controller.record_event, event='stim_onset')
    # collect looking time
    lt = controller.collect_lt(10, 2)
    target.setAutoDraw(False)
    win.callOnFlip(controller.record_event, event='stim_offset')
    print('Looking time in {tar}:{lt}'.format(tar=target.name, lt=lt))

# stop recording
controller.stop_recording()
# close the file
controller.close()

win.close()
core.quit()
