import os
import types

import numpy as np
from psychopy import core, event, sound, visual

from psychopy_tobii_infant import TobiiInfantController

###############################################################################
# Constants
DIR = os.path.dirname(__file__)
# users should know the display well.
DISPSIZE = (1280, 1024)
# define calibration points
CALINORMP = [(-0.4, 0.4), (-0.4, -0.4), (0.0, 0.0), (0.4, 0.4), (0.4, -0.4)]
CALIPOINTS = [(x * DISPSIZE[0], y * DISPSIZE[1]) for x, y in CALINORMP]
# stimuli to use in calibration
# The number of stimuli must be the same or larger than the calibration points.
CALISTIMS = [
    'infant/{}'.format(x) for x in os.listdir(os.path.join(DIR, 'infant'))
    if x.endswith('.png') and not x.startswith('.')
]
SOUNDSTIM = 'infant/wawa.wav'

###############################################################################
# Demo
# create a Window to control the monitor
win = visual.Window(size=[1280, 1024],
                    units='pix',
                    fullscr=True,
                    allowGUI=False)

# prepare the audio stimuli used in calibration
audio_grabber = sound.Sound(SOUNDSTIM)

# setup the attention grabber during adjusting the participant's position
grabber = visual.MovieStim3(win, "infant/seal-clip.mp4")


# create a customized calibration procedure with sound
# code snippets copied from _update_calibration_infant()
def customized_update_calibration(self,
                                  _focus_time=0.5,
                                  collect_key='space',
                                  exit_key='return'):
    # start calibration
    event.clearEvents()
    point_idx = -1
    in_calibration = True
    clock = core.Clock()
    while in_calibration:
        # get keys
        keys = event.getKeys()
        for key in keys:
            if key in self.numkey_dict:
                point_idx = self.numkey_dict[key]
                # -- Modification begin --
                # play the sound
                if point_idx in self.retry_points:
                    audio_grabber.play()
                # -- Modification end --
            elif key == collect_key:
                # allow the participant to focus
                core.wait(_focus_time, 0.0)
                # collect samples when space is pressed
                if point_idx in self.retry_points:
                    self._collect_calibration_data(
                        self.original_calibration_points[point_idx])
                    point_idx = -1
                    # -- Modification begin --
                    # stop the sound after collection of calibration data
                    audio_grabber.stop()
                    # -- Modification end --
            elif key == exit_key:
                # exit calibration when return is presssed
                in_calibration = False
                break

        # draw calibration target
        if point_idx in self.retry_points:
            this_target = self.targets.get_stim(point_idx)
            this_pos = self.original_calibration_points[point_idx]
            this_target.setPos(this_pos)
            t = clock.getTime() * self.shrink_speed
            newsize = [
                (np.sin(t)**2 + self.calibration_target_min) * e
                for e in self.targets.get_stim_original_size(point_idx)
            ]
            this_target.setSize(newsize)
            this_target.draw()
        self.win.flip()


# initialize TobiiInfantController to communicate with the eyetracker
controller = TobiiInfantController(win)
# use the customized calibration
controller.update_calibration = types.MethodType(customized_update_calibration,
                                                 controller)

# setup the attention grabber during adjusting the participant's position
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

marker = visual.Rect(win, width=20, height=20, autoLog=False)

# Start recording.
# filename of the data file could be define in this method or when creating an
# TobiiInfantController instance
controller.start_recording('demo5-test.tsv')
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
