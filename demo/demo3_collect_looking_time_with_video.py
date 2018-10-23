#!/usr/bin/env python
import os

from psychopy import visual, event, core, prefs
prefs.general['audioLib'] = ['sounddevice']

from psychopy_tobii_infant import infant_tobii_controller

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
    if '.png' in x
]

###############################################################################
# Demo
# create a Window to control the monitor
win = visual.Window(
    size=[1280, 1024],
    units='pix',
    screen=2, # change it to the real monitor
    fullscr=True,
    allowGUI=False)

# initialize tobii_controller to communicate with the eyetracker
controller = infant_tobii_controller(win)

# show the relative position of the subject to the eyetracker
# Press space to exit
controller.show_status("infant/seal-clip.mp4")

# How to use:
# - Use 1~9 (depending on the number of calibration points) to present
#   calibration stimulus and 0 to hide the target.
# - Press space to start collect calibration samples.
# - Press return (Enter) to finish the calibration and show the result.
# - Choose the points to recalibrate with 1~9.
# - Press decision_key to accept the calibration or recalibrate.
success = controller.run_calibration(CALIPOINTS, CALISTIMS)
if not success:
    core.quit()

# prepare the video
movie = visual.MovieStim3(
    win,
    'infant/seal-clip.mp4',
    size=[600, 600],
    units='pix',
    loop=True,
    name='infant/seal-clip.mp4')

# Start recording.
# filename of the data file could be define in this method or when creating an
# infant_tobii_controller instance
controller.start_recording('demo3-test.tsv')

# start
# let the monitor draw the movie automatically
movie.setAutoDraw(True)
lt = controller.collect_lt_mov(movie, 10, 2)
print('Looking time: %.3fs' % lt)
# when finish, remove the movie
movie.setAutoDraw(False)

# stop recording
controller.stop_recording()
# close the file
controller.close()

core.quit()
