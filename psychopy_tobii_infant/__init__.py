import math
import random
import tobii_research
import psychopy_tobii_controller
import numpy as np
import time

from psychopy import visual, event, core
from psychopy.constants import PY3

try:
    import Image
    import ImageDraw
except:
    from PIL import Image
    from PIL import ImageDraw

# check python version
if PY3:
    import types


class infant_tobii_controller(psychopy_tobii_controller.tobii_controller):

    infant_stims = None

    # inherit the methods from tobii_controller
    def __init__(self, win, id=0):
        self.eyetracker_id = id
        self.win = win
        self.update_calibration = self.update_calibration_infant

        eyetrackers = tobii_research.find_all_eyetrackers()

        if len(eyetrackers) == 0:
            raise RuntimeError('No Tobii eyetrackers')

        try:
            self.eyetracker = eyetrackers[self.eyetracker_id]
        except:
            raise ValueError(
                'Invalid eyetracker ID {}\n({} eyetrackers found)'.format(
                    self.eyetracker_id, len(eyetrackers)))

        self.calibration = tobii_research.ScreenBasedCalibration(
            self.eyetracker)

    def on_gaze_data_status(self, gaze_data):
        super().on_gaze_data_status(gaze_data)

    def run_calibration(self,
                        calibration_points,
                        infant_stims,
                        start_key='space',
                        decision_key='space',
                        enable_mouse=False):

        if self.eyetracker is None:
            raise RuntimeError('Eyetracker is not found.')

        if not (2 <= len(calibration_points) <= 9):
            raise ValueError('Calibration points must be 2~9')

        self.infant_stims = infant_stims

        img = Image.new('RGBA', tuple(self.win.size))
        img_draw = ImageDraw.Draw(img)

        result_img = visual.SimpleImageStim(self.win, img, autoLog=False)
        result_msg = visual.TextStim(
            self.win,
            pos=(0, -self.win.size[1] / 4),
            color='white',
            units='height',
            autoLog=False)
        remove_marker = visual.Circle(
            self.win,
            radius=0.01,
            fillColor='black',
            lineColor='white',
            lineWidth=1,
            units='height',
            autoLog=False)

        self.calibration.enter_calibration_mode()

        self.original_calibration_points = calibration_points[:]
        # set all points
        cp_num = len(self.original_calibration_points)
        self.retry_points = [*range(cp_num)]

        in_calibration_loop = True
        while in_calibration_loop:
            self.calibration_points = []
            for i in range(cp_num):
                if i in self.retry_points:
                    self.calibration_points.append(
                        self.original_calibration_points[i])

            event.clearEvents()
            if start_key is None and not enable_mouse:
                self.win.flip()
            else:
                if enable_mouse:
                    mouse = event.Mouse(visible=False, win=self.win)
                    result_msg.setText(
                                'Click left button to start calibration')
                    result_msg.draw()
                    self.win.flip()
                    while True:
                        if mouse.getPressed()[0]:
                            break
                # start is not None and enable_mouse is False
                else:
                    result_msg.setText(
                        'Press {} to start calibration'.format(start_key))
                    result_msg.draw()
                    self.win.flip()
                    event.waitKeys(keyList=[start_key])

            self.update_calibration()

            calibration_result = self.calibration.compute_and_apply()

            self.win.flip()

            img_draw.rectangle(
                ((0, 0), tuple(self.win.size)), fill=(0, 0, 0, 0))
            if calibration_result.status == tobii_research.CALIBRATION_STATUS_FAILURE:
                #computeCalibration failed.
                pass
            else:
                if len(calibration_result.calibration_points) == 0:
                    pass
                else:
                    for calibration_point in calibration_result.calibration_points:
                        p = calibration_point.position_on_display_area
                        for calibration_sample in calibration_point.calibration_samples:
                            lp = calibration_sample.left_eye.position_on_display_area
                            rp = calibration_sample.right_eye.position_on_display_area
                            if calibration_sample.left_eye.validity == tobii_research.VALIDITY_VALID_AND_USED:
                                img_draw.line(
                                    ((p[0] * self.win.size[0],
                                      p[1] * self.win.size[1]),
                                     (lp[0] * self.win.size[0],
                                      lp[1] * self.win.size[1])),
                                    fill=(0, 255, 0, 255))
                            if calibration_sample.right_eye.validity == tobii_research.VALIDITY_VALID_AND_USED:
                                img_draw.line(
                                    ((p[0] * self.win.size[0],
                                      p[1] * self.win.size[1]),
                                     (rp[0] * self.win.size[0],
                                      rp[1] * self.win.size[1])),
                                    fill=(255, 0, 0, 255))
                        img_draw.ellipse(
                            ((p[0] * self.win.size[0] - 3,
                              p[1] * self.win.size[1] - 3),
                             (p[0] * self.win.size[0] + 3,
                              p[1] * self.win.size[1] + 3)),
                            outline=(0, 0, 0, 255))

            if enable_mouse:
                result_msg.setText(
                    'Accept/Retry: right-click\n'
                    'Recalibrate all points: 0\n'
                    'Select recalibration points: 1-{p} key or left-click\n'
                    'Abort: esc'.format(p=cp_num))
            else:
                result_msg.setText(
                    'Accept/Retry: {k}\n'
                    'Recalibrate all points: 0\n'
                    'Select recalibration points: 1-{p} key\n'
                    'Abort: esc'.format(k=decision_key, p=cp_num))
            result_img.setImage(img)

            waitkey = True
            self.retry_points = []
            if enable_mouse:
                mouse.setVisible(True)
            event.clearEvents()
            while waitkey:
                for key in event.getKeys():
                    if key in [decision_key, 'escape']:
                        waitkey = False
                    elif key in ['0', 'num_0']:
                        if len(self.retry_points) == 0:
                            self.retry_points = list(
                                range(cp_num))
                        else:
                            self.retry_points = []
                    elif key in self.key_index_dict:
                        key_index = self.key_index_dict[key]
                        if key_index < cp_num:
                            if key_index in self.retry_points:
                                self.retry_points.remove(key_index)
                            else:
                                self.retry_points.append(key_index)
                if enable_mouse:
                    pressed = mouse.getPressed()
                    if pressed[2]:  # right click
                        key = decision_key
                        waitkey = False
                    elif pressed[0]:  # left click
                        mouse_pos = mouse.getPos()
                        for key_index in range(
                                cp_num):
                            p = self.original_calibration_points[key_index]
                            if np.linalg.norm([
                                    mouse_pos[0] - p[0], mouse_pos[1] - p[1]
                            ]) < self.calibration_target_dot.radius * 5:
                                if key_index in self.retry_points:
                                    self.retry_points.remove(key_index)
                                else:
                                    self.retry_points.append(key_index)
                                time.sleep(0.2)
                                break
                result_img.draw()
                if len(self.retry_points) > 0:
                    for index in self.retry_points:
                        if index > cp_num:
                            self.retry_points.remove(index)
                        remove_marker.setPos(
                            self.original_calibration_points[index])
                        remove_marker.draw()
                result_msg.draw()
                self.win.flip()

            if key == decision_key:
                if len(self.retry_points) == 0:
                    retval = 'accept'
                    in_calibration_loop = False
                else:  #retry
                    for point_index in self.retry_points:
                        x, y = self.get_tobii_pos(
                            self.original_calibration_points[point_index])
                        self.calibration.discard_data(x, y)
            elif key == 'escape':
                retval = 'abort'
                in_calibration_loop = False
            else:
                raise RuntimeError('Calibration: Invalid key')

            if enable_mouse:
                mouse.setVisible(False)

        self.calibration.leave_calibration_mode()

        if enable_mouse:
            mouse.setVisible(False)

        return retval

    def collect_calibration_data(self, p, cood='PsychoPy'):
        super().collect_calibration_data(p, cood='PsychoPy')

    def subscribe(self):
        super().subscribe()

    def unsubscribe(self):
        super().unsubscribe()

    def on_gaze_data(self, gaze_data):
        super().on_gaze_data(gaze_data)

    def get_current_gaze_position(self):
        return super().get_current_gaze_position()

    def get_current_pupil_size(self):
        return super().get_current_pupil_size()

    def open_datafile(self, filename, embed_events=False):
        super().open_datafile(filename, embed_events=False)

    def close_datafile(self):
        super().close_datafile()

    def record_event(self, event):
        super().record_event(event)

    def flush_data(self):
        super().flush_data()

    def get_psychopy_pos(self, p):
        return super().get_psychopy_pos(p)

    def get_tobii_pos(self, p):
        return super().get_tobii_pos(p)

    def convert_tobii_record(self, record, start_time):
        return super().convert_tobii_record(record, start_time)

    def interpolate_gaze_data(self, record1, record2, t):
        return super().interpolate_gaze_data(record1, record2, t)

    def show_status(self,
                    att_stim,
                    enable_mouse=False,
                    pos=[0, 0],
                    size=[640, 480],
                    units='pix'):
        """Infant-friendly procedure to adjust the participant's position.

        This is an implementation of show_status() in psychopy_tobii_controller. It
        plays an interesting video to attract the participant's attention and
        map the relative position of eyes to the track box. The experimenter can
        thus inspect and adjust the position of the participant.

        Args:
            att_stim: the video to be played.
            enable_mouse: use mouse clicks to leave the procedure?
            pos: the position to draw the video.
            size: the size of the video.
            units: the units of parameters (see PsychoPy manual for more info).

        Returns:
            None
        """
        attention_grabber = visual.MovieStim3(
            self.win,
            att_stim,
            pos=pos,
            size=size,
            units=units,
            name=att_stim,
            autoLog=False)

        bgrect = visual.Rect(
            self.win,
            pos=(0, 0.4),
            width=0.25,
            height=0.2,
            lineColor='white',
            fillColor='black',
            units='height',
            autoLog=False)

        leye = visual.Circle(
            self.win,
            size=0.02,
            units='height',
            lineColor=None,
            fillColor='green',
            autoLog=False)

        reye = visual.Circle(
            self.win,
            size=0.02,
            units='height',
            lineColor=None,
            fillColor='red',
            autoLog=False)

        zbar = visual.Rect(
            self.win,
            pos=(0, 0.28),
            width=0.25,
            height=0.03,
            lineColor='green',
            fillColor='green',
            units='height',
            autoLog=False)

        zc = visual.Rect(
            self.win,
            pos=(0, 0.28),
            width=0.01,
            height=0.03,
            lineColor='white',
            fillColor='white',
            units='height',
            autoLog=False)

        zpos = visual.Rect(
            self.win,
            pos=(0, 0.28),
            width=0.009,
            height=0.03,
            lineColor='black',
            fillColor='black',
            units='height',
            autoLog=False)

        if self.eyetracker is None:
            raise RuntimeError('Eyetracker is not found.')

        if enable_mouse:
            mouse = event.Mouse(visible=False, win=self.win)

        self.gaze_data_status = None
        self.eyetracker.subscribe_to(tobii_research.EYETRACKER_GAZE_DATA,
                                     self.on_gaze_data_status)
        att_timer = core.CountdownTimer(attention_grabber.duration)
        playing = True
        b_show_status = True
        while b_show_status:
            attention_grabber.play()
            att_timer.reset()
            while att_timer.getTime() > 0 and playing:
                bgrect.draw()
                zbar.draw()
                zc.draw()
                if self.gaze_data_status is not None:
                    lp, lv, rp, rv = self.gaze_data_status
                    if lv:
                        leye.setPos(((lp[0] - 0.5) * 0.2,
                                     ((lp[1] - 0.5) * 0.2 + 0.4)))
                        leye.draw()
                    if rv:
                        reye.setPos(((rp[0] - 0.5) * 0.2,
                                     ((rp[1] - 0.5) * 0.2 + 0.4)))
                        reye.draw()
                    if lv or rv:
                        zpos.setPos(((((lp[2] * int(lv) + rp[2] * int(rv)) /
                                       (int(lv) + int(rv))) - 0.5) * 0.125,
                                     0.28))
                        zpos.draw()

                for key in event.getKeys():
                    if key == 'escape' or key == 'space':
                        b_show_status = False
                        playing = False
                        break

                if enable_mouse and mouse.getPressed()[0]:
                    b_show_status = False
                    playing = False

                attention_grabber.draw()
                self.win.flip()
            if b_show_status:
                attention_grabber.loadMovie(att_stim)

        attention_grabber.stop()
        self.eyetracker.unsubscribe_from(tobii_research.EYETRACKER_GAZE_DATA)

    def update_calibration_infant(self, collect_key='space',
                                  exit_key='return'):
        """Five-point calibration for infants.

        An implementation of run_calibration() in psychopy_tobii_controller,
        Using 1~9 to present calibration stimulus and 0 to hide the target.

        Args:
            collect_key: key to start collecting samples.
            exit_key: key to finish and leave the current calibration procedure.

        Returns:
            None
        """

        # the keymap for target index
        numkey_dict = {
            'num_0': -1,
            'num_1': 0,
            'num_2': 1,
            'num_3': 2,
            'num_4': 3,
            'num_5': 4,
            'num_6': 5,
            'num_7': 7,
            'num_8': 8,
            'num_9': 9
        }

        current_point_index = -1
        # prepare calibration stimuli
        cali_targets = [
            visual.ImageStim(self.win, image=v) for v in self.infant_stims
        ]
        # randomization of calibration targets (to entartain the infants hopefully...)
        random.shuffle(cali_targets)

        # start calibration
        in_calibration = True
        # fix_oval
        win_r = self.win.size[0] / self.win.size[1]
        clock = core.Clock()
        event.clearEvents()
        while in_calibration:
            # get keys
            keys = event.getKeys()
            for key in keys:
                if key in numkey_dict:
                    current_point_index = numkey_dict[key]
                elif key == collect_key:
                    # collect samples when space is pressed
                    if current_point_index in self.retry_points:
                        self.collect_calibration_data(
                            self.calibration_points[current_point_index])
                        # deactivate the target after colleting samples
                        current_point_index = -1
                elif key == exit_key:
                    # exit calibration when return is presssed
                    in_calibration = False
                    break

            # draw calibration target
            if 0 <= current_point_index <= 4:
                cali_targets[current_point_index].setPos(
                    self.original_calibration_points[current_point_index])
                t = clock.getTime()
                newsize = [2 - math.sin(2 * t) * e for e in [1, win_r]]
                cali_targets[current_point_index].setSize(
                    newsize, units='norm')
                cali_targets[current_point_index].draw()
            self.win.flip()

    def get_current_gaze_validity(self):
        """Get gaze validity.

        Get current gaze validity provided by Tobii eye tracker as a tuple of
        (left_validity, right_validity). Users may not call this function.

        Args:
            None
        Returns:
            lv: validity of left-eye gaze point
            rv: validity of right-eye gaze point
        """

        if len(self.gaze_data) == 0:
            return (np.nan, np.nan)
        else:
            lv = self.gaze_data[-1][4]
            rv = self.gaze_data[-1][8]
            return (lv, rv)

    # Collect looking time
    def collect_lt(self, max_time, min_away, blink_dur=1):
        """Collect looking time data in runtime

        Collect and calculate looking time in runtime. Also end the trial
        automatically when the participant look away.

        Args:
            max_time: maximum looking time in seconds.
            min_away: minimum duration to stop in seconds.
            blink_dur: the tolerable duration of missing data in seconds.

        Returns:
            the looking time in the trial.
        """

        trial_timer = core.CountdownTimer(max_time)
        absence_timer = core.CountdownTimer(min_away)
        away = []
        looking = True
        trial_timer.reset()
        while trial_timer.getTime() > 0 and looking:
            lv, rv = self.get_current_gaze_validity()
            if not any((lv, rv)):
                # consecutive invalid samples will be counted
                absence_timer.reset()
                while absence_timer.getTime() > 0:
                    if any((lv, rv)):
                        # if the loss is less than blink_dur, it's probabliy a blink
                        if absence_timer.getTime() >= (min_away - blink_dur):
                            break
                        # save the looking away time for looking time calculation
                        else:
                            away.append(min_away - absence_timer.getTime())
                            break
                else:
                    # calculate the correct looking time
                    lt = max_time - trial_timer.getTime() - np.sum(
                        away) - min_away
                    # leave the trial when looking away
                    looking = False
                    return (round(lt, 3))
        # if the loop is completed, return the maximum looking time
        else:
            lt = max_time - np.sum(away)
            return (round(lt, 3))
