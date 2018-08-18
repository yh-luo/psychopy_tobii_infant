# collect looking time while playing a video
import random
import os

from psychopy import visual, event, core, prefs
prefs.general['audioLib'] = ['sounddevice']

from psychopy_tobii_infant import infant_tobii_controller

###############################################################################
# Constants
###############################################################################
random.seed()

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
# It is assumed that the profile of the monitor is know. Thus, stimuli in
# show_status are in 'height' units.
win = visual.Window(
    size=[1280, 1024],
    monitor='tobii',
    units='cm',
    screen=1,
    fullscr=True,
    allowGUI=False)

# initialize tobii_controller to communicate with the eyetracker
controller = infant_tobii_controller(win)
# Open a file to save the eyetracking data
controller.open_datafile('test_infant_calibration.tsv')

# show the relative position of the subject to the eyetracker
controller.show_status("infant/elmo's ducks.mp4")

ret = controller.run_calibration(CALIPOINTS, CALISTIMS, start_key=None)

if ret == 'abort':
    core.quit()

# prepare the video
movie = visual.MovieStim3(
    win,
    'infant/v1_h_r.mp4',
    size=[600, 600],
    units='pix',
    loop=True,
    name='infant/v1_h_r.mp4')

controller.subscribe()
# wait a bit for the eyetracker to turn on
core.wait(0.5)

# start
# it's the requisite to use collect_lt_mov:
# let the monitor draw the movie automatically
movie.setAutoDraw(True)
lt = controller.collect_lt_mov(movie, 10, 2)
print('Looking time: %.3fs' % lt)
# when finish, remove the movie
movie.setAutoDraw(False)
# reload the video if it will be used again
movie.loadMovie(movie.name)

# stop recording
controller.unsubscribe()
# close the file
controller.close_datafile()

win.close()
core.quit()
