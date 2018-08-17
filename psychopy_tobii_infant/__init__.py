import math
import random
import tobii_research
import psychopy_tobii_controller
import numpy as np

from psychopy import visual, event, core

try:
    import Image
    import ImageDraw
except:
    from PIL import Image
    from PIL import ImageDraw


class infant_tobii_controller(psychopy_tobii_controller.tobii_controller):
    """Tobii controller for PsychoPy.

    psychopy_tobii_controller and tobii_research are required for this module.

    Args:
        win: psychopy.visual.Window object.
        id: the id of eyetracker.

    Attributes:
        infant_stims: the stimuli to be used in calibration. The user should
            define it with run_calibration().
        numkey_dict: the keymap to index calibration target.
        eyetracker_id: the id of eyetracker.
        win: psychopy.visual.Window object.
        update_calibration: the used calibration procedure.
        eyetracker: the used eyetracker.
        calibration: the calibration procedure from tobii_research.
        targets: the stimuli in calibration.
        target_original_size: the original size of the targets. It assumes that
            all the targets are of the same size.
        original_calibration_points: calibration points defined by The user in
            run_calibration().
        retry_points: recalibration points defined by The user in calibration.
        calibration_points: the current calibration point.
        gaze_data_status: the current gaze position, used by show_status().
    """

    infant_stims = None
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

    def run_calibration(self,
                        calibration_points,
                        infant_stims,
                        start_key=None,
                        decision_key='space'):
        """Run calibration

        The experimenter should manually show the stimulus and collect data
        when the subject is paying attention to the stimulus.
        The stimulus will change its size according to time, in order to
        attract the infant. The experimenter may press the `start_key` to start
        the procedure. To finish and leave the procedure, press the
        `decision_key`.

        Args:
            calibration_points: list of position of the calibration points.
            infant_stims: list of images to attract the infant.
            start_key: the key to start the procedure. If None, directly
            proceed to the calibration procedure.
            decision_key: the key to leave the procedure.

        Returns:
            retval: the state of calibration
        """
        if self.eyetracker is None:
            raise RuntimeError('Eyetracker is not found.')

        if not (2 <= len(calibration_points) <= 9):
            raise ValueError('Calibration points must be 2~9')

        # prepare calibration stimuli
        self.targets = [
            visual.ImageStim(self.win, image=v, autoLog=False)
            for v in infant_stims
        ]
        # get original size of stimuli
        self.target_original_size = self.targets[0].size
        img = Image.new('RGBA', tuple(self.win.size))
        img_draw = ImageDraw.Draw(img)

        result_img = visual.SimpleImageStim(self.win, img, autoLog=False)
        result_msg = visual.TextStim(
            self.win,
            pos=(0, -self.win.size[1] / 4),
            color='white',
            units='pix',
            autoLog=False)
        retry_marker = visual.Circle(
            self.win,
            radius=0.1 * self.target_original_size[0],
            fillColor='black',
            lineColor='white',
            lineWidth=1,
            autoLog=False)

        self.calibration.enter_calibration_mode()

        self.original_calibration_points = calibration_points[:]
        # set all points
        cp_num = len(self.original_calibration_points)
        self.retry_points = [*range(cp_num)]

        in_calibration_loop = True
        event.clearEvents()
        while in_calibration_loop:

            # randomization of calibration targets (to entartain the infants hopefully...)
            random.shuffle(self.targets)
            self.calibration_points = [
                self.original_calibration_points[x] for x in self.retry_points
            ]

            if start_key is None:
                self.win.flip()
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

            result_msg.setText(
                'Accept/Retry: {k}\n'
                'Select/Deselect all points: 0\n'
                'Select/Deselect recalibration points: 1-{p} key\n'
                'Abort: esc'.format(k=decision_key, p=cp_num))
            result_img.setImage(img)

            waitkey = True
            self.retry_points = []
            while waitkey:
                for key in event.getKeys():
                    if key in [decision_key, 'escape']:
                        waitkey = False
                    elif key in ['0', 'num_0']:
                        if len(self.retry_points) == cp_num:
                            self.retry_points = []
                        else:
                            self.retry_points = [*range(cp_num)]
                    elif key in self.numkey_dict:
                        key_index = self.numkey_dict[key]
                        if key_index < cp_num:
                            if key_index in self.retry_points:
                                self.retry_points.remove(key_index)
                            else:
                                self.retry_points.append(key_index)

                result_img.draw()
                if len(self.retry_points) > 0:
                    for retry_p in self.retry_points:
                        retry_marker.setPos(
                            self.original_calibration_points[retry_p])
                        retry_marker.draw()

                result_msg.draw()
                self.win.flip()

            if key == decision_key:
                if len(self.retry_points) == 0:
                    retval = 'accept'
                    in_calibration_loop = False
                else:  # retry
                    for point_index in self.retry_points:
                        x, y = self.get_tobii_pos(
                            self.original_calibration_points[point_index])
                        self.calibration.discard_data(x, y)
            elif key == 'escape':
                retval = 'abort'
                in_calibration_loop = False
            else:
                raise RuntimeError('Calibration: Invalid key')

        self.calibration.leave_calibration_mode()

        return retval

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
            width=0.008,
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
        """The calibration procedure designed for infants.

        An implementation of run_calibration() in psychopy_tobii_controller,
        Using 1~9 to present calibration stimulus and 0 to hide the target.

        Args:
            collect_key: the key to start collecting samples.
            exit_key: the key to finish and leave the current calibration 
                procedure. It should not be confused with `decision_key`, which
                is used to leave the whole calibration process. `exit_key` is
                used to leave the current calibration, the user may recalibrate
                or accept the results afterwards.

        Returns:
            None
        """

        # start calibration
        event.clearEvents()
        current_point_index = -1
        in_calibration = True
        clock = core.Clock()
        while in_calibration:
            # get keys
            keys = event.getKeys()
            for key in keys:
                if key in self.numkey_dict:
                    current_point_index = self.numkey_dict[key]
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
            if current_point_index in self.retry_points:
                self.targets[current_point_index].setPos(
                    self.original_calibration_points[current_point_index])
                t = clock.getTime()
                newsize = [(math.sin(t)**2 + 0.2) * e
                           for e in self.target_original_size]
                self.targets[current_point_index].setSize(newsize)
                self.targets[current_point_index].draw()
            self.win.flip()

    def get_current_gaze_validity(self):
        """Get gaze validity.

        Get current gaze validity provided by Tobii eye tracker as a tuple of
        (left_validity, right_validity). The user may not call this function.

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
            lt: The looking time in the trial.
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
            self.win.flip()
        # if the loop is completed, return the maximum looking time
        else:
            lt = max_time - np.sum(away)
            return (round(lt, 3))

    # inherit the methods from tobii_controller
    def on_gaze_data_status(self, gaze_data):
        super().on_gaze_data_status(gaze_data)

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
