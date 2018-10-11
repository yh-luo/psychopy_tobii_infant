import math
import tobii_research as tr
import numpy as np
import datetime
import os

from psychopy import visual, event, core
from psychopy.tools.monitorunittools import deg2cm, deg2pix, pix2cm, pix2deg, cm2pix
from psychopy.constants import FINISHED

try:
    import Image
    import ImageDraw
except:
    from PIL import Image
    from PIL import ImageDraw


class infant_tobii_controller:
    """Tobii controller for PsychoPy.

    tobii_research are required for this module.

    Args:
        win: psychopy.visual.Window object.
        id: the id of eyetracker.
        filename: the name of the data file.

    Attributes:
        infant_stims: the stimuli to be used in calibration. The user should
            define it with run_calibration().
        numkey_dict: the keymap to index calibration target.
        eyetracker_id: the id of eyetracker.
        win: psychopy.visual.Window object.
        eyetracker: the used eyetracker.
        calibration: the calibration procedure from tobii_research.
        update_calibration: the used calibration procedure.
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
        'num_7': 6,
        'num_8': 7,
        'num_9': 8
    }

    def __init__(self, win, id=0, filename='gaze_TOBII_output.tsv'):
        self.eyetracker_id = id
        self.win = win
        self.filename = filename
        eyetrackers = tr.find_all_eyetrackers()

        if len(eyetrackers) == 0:
            raise RuntimeError('No Tobii eyetrackers')

        try:
            self.eyetracker = eyetrackers[self.eyetracker_id]
        except:
            raise ValueError(
                'Invalid eyetracker ID {}\n({} eyetrackers found)'.format(
                    self.eyetracker_id, len(eyetrackers)))

        self.calibration = tr.ScreenBasedCalibration(self.eyetracker)
        self.update_calibration = self._update_calibration_infant
        self.gaze_data = []

    def _on_gaze_data(self, gaze_data):
        """Callback function used by Tobii SDK.

            Users should not use this method on most occasions.

        Args:
            gaze_data: gaze data provided by the eye tracker.

        Returns:
            None
        """
        self.gaze_data.append(gaze_data)

    def _get_psychopy_pos(self, p):
        """Convert Tobii ADCS coordinates to PsychoPy coordinates.

        Args:
            p: Gaze position (x, y) in Tobii ADCS.

        Returns:
            Gaze position in PsychoPy coordinate systems.
        """

        if self.win.units == 'norm':
            return (2 * p[0] - 1, -2 * p[1] + 1)
        elif self.win.units == 'height':
            return ((p[0] - 0.5) * (self.win.size[0] / self.win.size[1]),
                    -p[1] + 0.5)
        elif self.win.units in ['pix', 'cm', 'deg', 'degFlat', 'degFlatPos']:
            p_pix = ((p[0] - 0.5) * self.win.size[0],
                     (-p[1] + 0.5) * self.win.size[1])
            if self.win.units == 'pix':
                return p_pix
            elif self.win.units == 'cm':
                return (pix2cm(p_pix[0], self.win.monitor),
                        pix2cm(p_pix[1], self.win.monitor))
            elif self.win.units == 'deg':
                return (pix2deg(p_pix[0], self.win.monitor),
                        pix2deg(p_pix[1], self.win.monitor))
            else:
                return (pix2deg(
                    np.array(p_pix), self.win.monitor, correctFlat=True))
        else:
            raise ValueError('unit ({}) is not supported.'.format(
                self.win.units))

    def _get_tobii_pos(self, p):
        """Convert PsychoPy coordinates to Tobii ADCS coordinates.

        Args:
            p: Gaze position (x, y) in PsychoPy coordinate systems.

        Returns:
            Gaze position in Tobii ADCS.
        """

        if self.win.units == 'norm':
            return ((p[0] + 1) / 2, (p[1] - 1) / -2)
        elif self.win.units == 'height':
            return (p[0] * (self.win.size[1] / self.win.size[0]) + 0.5,
                    -p[1] + 0.5)
        elif self.win.units == 'pix':
            return self._pix2tobii(p)
        elif self.win.units in ['cm', 'deg', 'degFlat', 'degFlatPos']:
            if self.win.units == 'cm':
                p_pix = (cm2pix(p[0], self.win.monitor),
                         cm2pix(p[1], self.win.monitor))
            elif self.win.units == 'deg':
                p_pix = (deg2pix(p[0], self.win.monitor),
                         deg2pix(p[1], self.win.monitor))
            elif self.win.units in ['degFlat', 'degFlatPos']:
                p_pix = (deg2pix(
                    np.array(p), self.win.monitor, correctFlat=True))

            return self._pix2tobii(p_pix)
        else:
            raise ValueError('unit ({}) is not supported'.format(
                self.win.units))

    def _pix2tobii(self, p):
        """Convert PsychoPy pixel coordinates to Tobii ADCS.

            Called by _get_tobii_pos.

        Args:
            p: Gaze position (x, y) in pix.

        Returns:
            Gaze position in Tobii ADCS.
        """
        return (p[0] / self.win.size[0] + 0.5, -p[1] / self.win.size[1] + 0.5)

    def _get_psychopy_pos_from_trackbox(self, p, units=None):
        """Convert Tobii TBCS coordinates to PsychoPy coordinates.

            Called by show_status.

        Args:
            p: Gaze position (x, y) in Tobii TBCS.
            units: The PsychoPy coordinate system to use.

        Returns:
            Gaze position in PsychoPy coordinate systems.
        """

        if units is None:
            units = self.win.units

        if units == 'norm':
            return (-2 * p[0] + 1, -2 * p[1] + 1)
        elif units == 'height':
            return ((-p[0] + 0.5) * (self.win.size[0] / self.win.size[1]),
                    -p[1] + 0.5)
        elif units in ['pix', 'cm', 'deg', 'degFlat', 'degFlatPos']:
            p_pix = ((-2 * p[0] + 1) * self.win.size[0] / 2,
                     (-2 * p[1] + 1) * self.win.size[1] / 2)
            if units == 'pix':
                return p_pix
            elif units == 'cm':
                return (pix2cm(p_pix[0], self.win.monitor),
                        pix2cm(p_pix[1], self.win.monitor))
            elif units == 'deg':
                return (pix2deg(p_pix[0], self.win.monitor),
                        pix2deg(p_pix[1], self.win.monitor))
            else:
                return (pix2deg(
                    np.array(p_pix), self.win.monitor, correctFlat=True))
        else:
            raise ValueError('unit ({}) is not supported.'.format(
                self.win.units))

    def _update_calibration_infant(self,
                                   collect_key='space',
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
                        self._collect_calibration_data(
                            self.original_calibration_points[
                                current_point_index])
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

    def _flush_to_file(self):
        """Write data to disk.

        Args:
            None

        Returns:
            None
        """
        self.datafile.flush()  # internal buffer to RAM
        os.fsync(self.datafile.fileno())  # RAM file cache to disk

    def _write_header(self):
        """Write the header to the data file.

        Args:
            None

        Returns:
            None
        """
        if self.embed_event:
            self.datafile.write('\t'.join([
                'TimeStamp', 'GazePointXLeft', 'GazePointYLeft',
                'ValidityLeft', 'GazePointXRight', 'GazePointYRight',
                'ValidityRight', 'GazePointX', 'GazePointY', 'PupilSizeLeft',
                'PupilValidityLeft', 'PupilSizeRight', 'PupilValidityRight',
                'Event'
            ]) + '\n')
        else:
            self.datafile.write('\t'.join([
                'TimeStamp', 'GazePointXLeft', 'GazePointYLeft',
                'ValidityLeft', 'GazePointXRight', 'GazePointYRight',
                'ValidityRight', 'GazePointX', 'GazePointY', 'PupilSizeLeft',
                'PupilValidityLeft', 'PupilSizeRight', 'PupilValidityRight'
            ]) + '\n')
        self._flush_to_file()

    def _write_event(self, record=None):
        """Write events to the data file.

        Args:
            record: reformed gaze data. Defaults to None
        Returns:
            None
        """

        # else:
        # check record
        if record is None:
            print('record not found. Write the events separately')
            self.embed_event = False
        else:
            for event in self.event_data:
                if event[0] <= record[0]:
                    self.datafile.write('%s\n' % event[1])
                    # remove the old event
                    self.event_data.remove(event)
                    break
            else:
                self.datafile.write('\n')

    def _write_record(self, record):
        """Write the Tobii output to the data file.

        Args:
            record: reformed gaze data

        Returns:
            None
        """
        format_string = (
            '%.1f\t'  # TimeStamp
            '%.4f\t'  # GazePointXLeft
            '%.4f\t'  # GazePointYLeft
            '%d\t'  # ValidityLeft
            '%.4f\t'  # GazePointXRight
            '%.4f\t'  # GazePointYRight
            '%d\t'  # ValidityRight
            '%.4f\t'  # GazePointX
            '%.4f\t'  # GazePointY
            '%.4f\t'  # PupilSizeLeft
            '%d\t'  # PupilValidityLeft
            '%.4f\t'  # PupilSizeRight
            '%d\t'  # PupilValidityRight
        )
        # write data
        self.datafile.write(format_string % record)

    def _convert_tobii_record(self, record):
        """Convert tobii coordinates to output style.

        Args:
            record: raw gaze data

        Returns:
            reformed gaze data
        """

        lp = self._get_psychopy_pos(record['left_gaze_point_on_display_area'])
        rp = self._get_psychopy_pos(record['right_gaze_point_on_display_area'])

        if not (record['left_gaze_point_validity']
                or record['right_gaze_point_validity']):  # not detected
            ave = (np.nan, np.nan)
        elif not record['left_gaze_point_validity']:
            ave = rp  # use right eye
        elif not record['right_gaze_point_validity']:
            ave = lp  # use left eye
        else:
            ave = ((lp[0] + rp[0]) / 2.0, (lp[1] + rp[1]) / 2.0)

        return (((record['system_time_stamp'] - self.t0) / 1000.0, lp[0],
                 lp[1], record['left_gaze_point_validity'], rp[0], rp[1],
                 record['right_gaze_point_validity'], ave[0], ave[1],
                 record['left_pupil_diameter'], record['left_pupil_validity'],
                 record['right_pupil_diameter'],
                 record['right_pupil_validity']))

    def _flush_data(self):
        """Wrapper for writing the header and data to the data file.

        Args:
            None

        Returns:
            None
        """
        if not self.gaze_data:
            # do nothing when there's no data
            return

        if self.recording:
            # do nothing while recording
            return

        self.datafile.write('Session Start\n')
        self._write_header()
        for gaze_data in self.gaze_data:
            output = self._convert_tobii_record(gaze_data)
            self._write_record(output)
            # if there's a corresponding event, write it.
            if self.event_data and self.embed_event:
                self._write_event(output)
        else:
            # write the remained events in the end of data
            for event in self.event_data:
                    self.datafile.write('%.1f\t%s\n' % (event[0], event[1]))
        self.datafile.write('Session End\n')
        self._flush_to_file()

    def _collect_calibration_data(self, p):
        """Callback function used by Tobii calibration in run_calibration.

        Args:
            p: the calibration point

        Returns:
            None
        """

        if self.calibration.collect_data(
                *self._get_tobii_pos(p)) != tr.CALIBRATION_STATUS_SUCCESS:
            self.calibration.collect_data(*self._get_tobii_pos(p))

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
            retval: the status of calibration
        """
        if self.eyetracker is None:
            raise RuntimeError('Eyetracker is not found.')

        if not (2 <= len(calibration_points) <= 9):
            raise ValueError('Calibration points must be 2~9')

        else:
            self.numkey_dict = {
                k: v
                for k, v in self.numkey_dict.items()
                if v < len(calibration_points)
            }

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
        self.retry_points = list(range(cp_num))

        in_calibration_loop = True
        event.clearEvents()
        while in_calibration_loop:

            # randomization of calibration targets
            np.random.shuffle(self.targets)
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
            if calibration_result.status == tr.CALIBRATION_STATUS_FAILURE:
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
                            if calibration_sample.left_eye.validity == tr.VALIDITY_VALID_AND_USED:
                                img_draw.line(
                                    ((p[0] * self.win.size[0],
                                      p[1] * self.win.size[1]),
                                     (lp[0] * self.win.size[0],
                                      lp[1] * self.win.size[1])),
                                    fill=(0, 255, 0, 255))
                            if calibration_sample.right_eye.validity == tr.VALIDITY_VALID_AND_USED:
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
                    elif key in self.numkey_dict:
                        if key in ['0', 'num_0']:
                            if len(self.retry_points) == cp_num:
                                self.retry_points = []
                            else:
                                self.retry_points = list(range(cp_num))
                        else:
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
                    retval = True
                    in_calibration_loop = False
                else:  # retry
                    for point_index in self.retry_points:
                        x, y = self._get_tobii_pos(
                            self.original_calibration_points[point_index])
                        self.calibration.discard_data(x, y)
            elif key == 'escape':
                retval = False
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
            units: the units of the video (see PsychoPy manual for more info).

        Returns:
            None
        """
        # to fix the audio
        visual.MovieStim3._unload = _unload
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

        self.eyetracker.subscribe_to(
            tr.EYETRACKER_GAZE_DATA, self._on_gaze_data, as_dictionary=True)
        core.wait(1)  # wait a bit for the eye tracker to get ready
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
                gaze_data = self.gaze_data[-1]
                lv = gaze_data['left_gaze_point_validity']
                rv = gaze_data['right_gaze_point_validity']
                lx, ly, lz = gaze_data[
                    'left_gaze_origin_in_trackbox_coordinate_system']
                rx, ry, rz = gaze_data[
                    'right_gaze_origin_in_trackbox_coordinate_system']
                if lv:
                    lx, ly = self._get_psychopy_pos_from_trackbox(
                        [lx, ly], units='height')
                    leye.setPos((lx * 0.25, ly * 0.2 + 0.4))
                    leye.draw()
                if rv:
                    rx, ry = self._get_psychopy_pos_from_trackbox(
                        [rx, ry], units='height')
                    reye.setPos((rx * 0.25, ry * 0.2 + 0.4))
                    reye.draw()
                if lv or rv:
                    zpos.setPos(((((lz * int(lv) + rz * int(rv)) /
                                   (int(lv) + int(rv))) - 0.5) * 0.125, 0.28))
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
        self.eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA)

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

        trial_timer = core.Clock()
        absence_timer = core.Clock()
        away_time = []

        looking = True
        trial_timer.reset()
        absence_timer.reset()

        while trial_timer.getTime() <= max_time:
            gaze_data = self.gaze_data[-1]
            lv = gaze_data['left_gaze_point_validity']
            rv = gaze_data['right_gaze_point_validity']

            if any((lv, rv)):
                # if the last sample is missing
                if not looking:
                    away_dur = absence_timer.getTime()
                    # if missing samples are larger than the threshold of termination
                    if away_dur >= min_away:
                        away_time.append(away_dur)
                        lt = trial_timer.getTime() - np.sum(away_time)
                        # stop the trial
                        return (round(lt, 3))
                    # if missing samples are larger than blink duration
                    elif away_dur >= blink_dur:
                        away_time.append(away_dur)
                    # if missing samples are tolerable
                    else:
                        pass
                looking = True
                absence_timer.reset()
            else:
                if absence_timer.getTime() >= min_away:
                    away_dur = absence_timer.getTime()
                    away_time.append(away_dur)
                    lt = trial_timer.getTime() - np.sum(away_time)
                    # terminate the trial
                    return (round(lt, 3))
                else:
                    pass
                looking = False

            self.win.flip()
        # if the loop is completed, return the looking time
        else:
            lt = max_time - np.sum(away_time)
            return (round(lt, 3))

    def collect_lt_mov(self, movie, max_time, min_away, blink_dur=1):
        """Collect looking time data and playing video

        Collect and calculate looking time in runtime. Also end the trial
        automatically when the participant look away.

        Args:
            movie: the MovieStim object to use.
            max_time: maximum looking time in seconds.
            min_away: minimum duration to stop in seconds.
            blink_dur: the tolerable duration of missing data in seconds.

        Returns:
            lt: The looking time in the trial.
        """

        trial_timer = core.Clock()
        absence_timer = core.Clock()
        away_time = []

        movie.play()
        looking = True
        trial_timer.reset()
        absence_timer.reset()
        while trial_timer.getTime() <= max_time:
            gaze_data = self.gaze_data[-1]
            lv = gaze_data['left_gaze_point_validity']
            rv = gaze_data['right_gaze_point_validity']

            if any((lv, rv)):
                # if the last sample is missing
                if not looking:
                    away_dur = absence_timer.getTime()
                    # if missing samples are larger than the threshold of termination
                    if away_dur >= min_away:
                        away_time.append(away_dur)
                        lt = trial_timer.getTime() - np.sum(away_time)
                        # stop the trial
                        movie.stop()
                        return (round(lt, 3))
                    # if missing samples are larger than blink duration
                    elif away_dur >= blink_dur:
                        away_time.append(away_dur)
                    # if missing samples are tolerable
                    else:
                        pass
                looking = True
                absence_timer.reset()
            else:
                if absence_timer.getTime() >= min_away:
                    away_dur = absence_timer.getTime()
                    away_time.append(away_dur)
                    lt = trial_timer.getTime() - np.sum(away_time)
                    # terminate the trial
                    movie.stop()
                    return (round(lt, 3))
                else:
                    pass
                looking = False

            movie.draw()
            self.win.flip()
        # if the loop is completed, return the looking time
        else:
            movie.stop()
            lt = max_time - np.sum(away_time)
            return (round(lt, 3))

    def start_recording(self, filename=None, newfile=True, embed_event=True):
        """Start recording

        Args:
            filename: the name of the data file. If None, use default name.
                Defaults to None.
            newfile: open a new file to save data. Defaults to True.
            embed_event: should the file contains the event column.
                Defaults to True.

        Returns:
            None
        """
        if filename is not None:
            if type(filename) == str:
                self.filename = filename
            else:
                raise ValueError('filename should be string')
        if newfile:
            self.open_datafile()

        self.embed_event = embed_event
        self.gaze_data = []
        self.event_data = []
        self.eyetracker.subscribe_to(
            tr.EYETRACKER_GAZE_DATA, self._on_gaze_data, as_dictionary=True)
        core.wait(1)  # wait a bit for the eye tracker to get ready
        self.recording = True
        self.t0 = tr.get_system_time_stamp()

    def stop_recording(self):
        """Stop recording.

        Args:
            None

        Returns:
            None
        """
        if self.recording:
            self.eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA)
            self.recording = False
            # time correction for event data
            self.event_data = list(
                map(lambda x: ((x[0] - self.t0) / 1000.0, x[1]),
                    self.event_data))
            self._flush_data()
        else:
            print('A recording has not been started. Do nothing now...')

    def subscribe(self):
        """Start recording (deprecated).

            Use start_recording instead.

        Args:
            None

        Returns:
            None
        """
        self.start_recording()

    def unsubscribe(self):
        """Stop recording (deprecated).

            Use stop_recording instead.

        Args:
            None

        Returns:
            None
        """
        self.stop_recording()

    def get_current_gaze_position(self):
        """Get the newest gaze position.

        Args:
            None

        Returns:
            ((left_eye_x, left_eye_y), (right_eye_x, right_eye_y))
        """

        if not self.gaze_data:
            return ((np.nan, np.nan), (np.nan, np.nan))
        else:
            lxy = (np.nan, np.nan)
            rxy = (np.nan, np.nan)
            gaze_data = self.gaze_data[-1]
            if gaze_data['left_gaze_point_validity']:
                lxy = self._get_psychopy_pos(
                    gaze_data["left_gaze_point_on_display_area"])
            if gaze_data['right_gaze_point_validity']:
                rxy = self._get_psychopy_pos(
                    gaze_data["right_gaze_point_on_display_area"])

            return (lxy, rxy)

    def get_current_pupil_size(self):
        """Get the newest recent pupil size.

        Args:
            None

        Returns:
            (left_eye_pupil_size, right_eye_pupil_size)
        """

        if not self.gaze_data:
            return (np.nan, np.nan)
        else:
            lp = np.nan
            rp = np.nan
            gaze_data = self.gaze_data[-1]
            if bool(gaze_data["left_pupil_validity"]):
                lp = gaze_data["left_pupil_diameter"]
            if bool(gaze_data["right_pupil_validity"]):
                rp = gaze_data["right_pupil_diameter"]

            return (lp, rp)

    def open_datafile(self):
        """Open a file for gaze data.

        Args:
            None

        Returns:
            None
        """
        try:
            self.close_datafile()
        except AttributeError:
            pass

        self.datafile = open(self.filename, 'w')
        self.datafile.write('Recording date:\t' +
                            datetime.datetime.now().strftime('%Y/%m/%d') +
                            '\n')
        self.datafile.write('Recording time:\t' +
                            datetime.datetime.now().strftime('%H:%M:%S') +
                            '\n')
        self.datafile.write(
            'Recording resolution:\t%d x %d\n' % tuple(self.win.size))

        self._flush_to_file()

    def close_datafile(self):
        """Close the data file.

        Args:
            None

        Returns:
            None
        """
        try:
            self.datafile.close()
        except AttributeError:
            raise AttributeError('No opened file to close.')

    def record_event(self, event):
        """Record events with timestamp.

        Note: This method works only during recording.

        Args:
            event: the event

        Returns:
            None
        """
        if not self.recording:
            return

        self.event_data.append([tr.get_system_time_stamp(), event])


def _unload(self):
    """Stop MovieStim3

    Fix the problem of audio stream in PsychoPy < v3.0

    """
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
