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

# prepare the experiment stimuli
tar_1 = visual.ImageStim(
    win,
    'stim/checkboard_big.png',
    size=[1280, 1024],
    units='pix',
    name='big')
tar_2 = visual.ImageStim(
    win,
    'stim/checkboard_small.png',
    size=[1280, 1024],
    units='pix',
    name='small')
alltar = [tar_1, tar_2]

# initialize tobii_controller to communicate with the eyetracker
controller = infant_tobii_controller(win)
# Open a file to save the eyetracking data
controller.open_datafile('test_infant_calibration.tsv')

# show the relative position of the subject to the eyetracker
controller.show_status("infant/elmo's ducks.mp4")

ret = controller.run_calibration(CALIPOINTS, CALISTIMS, start_key=None)

if ret == 'abort':
    core.quit()

controller.subscribe()
# wait a bit for the eyetracker to turn on
core.wait(0.5)
# start
random.shuffle(alltar)
for target in alltar:
    # Draw the stimuli in each frames
    target.setAutoDraw(True)
    stim_on = win.flip()
    # collect looking time
    lt = controller.collect_lt(10, 2)
    target.setAutoDraw(False)
    stim_off = win.flip()
    print('Looking time in {tar}:{lt}\nStim duration:{dur}'.format(
        tar=target.name, lt=lt, dur=stim_off - stim_on))

# stop recording
controller.unsubscribe()
# close the file
controller.close_datafile()

win.close()
core.quit()
