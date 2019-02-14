import tobii_research as tr
import numpy as np
import datetime
import os

from psychopy import visual, event, core, logging
from psychopy.tools.monitorunittools import deg2cm, deg2pix, pix2cm, pix2deg, cm2pix

from PIL import Image
from PIL import ImageDraw

default_calibration_dot_size = {
    'norm': 0.02,
    'height': 0.01,
    'pix': 10.0,
    'degFlatPos': 0.25,
    'deg': 0.25,
    'degFlat': 0.25,
    'cm': 0.25
}
default_calibration_disc_size = {
    'norm': 0.08,
    'height': 0.04,
    'pix': 40.0,
    'degFlatPos': 1.0,
    'deg': 1.0,
    'degFlat': 1.0,
    'cm': 1.0
}

default_key_index_dict = {
    "0": -1,
    'num_0': -1,
    "1": 0,
    'num_1': 0,
    "2": 1,
    'num_2': 1,
    "3": 2,
    'num_3': 2,
    "4": 3,
    'num_4': 3,
    "5": 4,
    'num_5': 4,
    "6": 5,
    'num_6': 5,
    "7": 6,
    'num_7': 6,
    "8": 7,
    'num_8': 7,
    "9": 8,
    'num_9': 8
}


class tobii_controller:

    _numkey_dict = default_key_index_dict.copy()
    _shrink_speed = 1.5
    _shrink_sec = 3 / _shrink_speed
    _calibration_dot_color = (0, 0, 0)
    _calibration_disc_color = (-1, -1, 0)
    _calibration_target_min = 0.2
    _update_calibration = None

    def __init__(self, win, id=0, filename='gaze_TOBII_output.tsv'):
        """Tobii controller for PsychoPy.

            tobii_research are required for this module.

        Args:
            win: psychopy.visual.Window object.
            id: the id of eyetracker.
            filename: the name of the data file.

        Attributes:
            shrink_speed: the shrinking speed of target in calibration.
                Defaults to 1.5.
            calibration_dot_size: the size of the central dot in the
                calibration target. Defaults to default_calibration_dot_size
                according to the units of self.win.
            calibration_dot_color: the color of the central dot in the
                calibration target. Defaults to grey.
            calibration_disc_size: the size of the disc in the
                calibration target. Defaults to default_calibration_disc_size
                according to the units of self.win.
            calibration_disc_color: the color of the disc in the
                calibration target. Defaults to deep blue.
            numkey_dict: keys used for calibration. Defaults to the number pad.
            update_calibration: the presentation of calibration target.
                Defaults to auto calibration.
        """
        self.eyetracker_id = id
        self.win = win
        self.filename = filename
        self._calibration_dot_size = default_calibration_dot_size[self.win.
                                                                  units]
        self._calibration_disc_size = default_calibration_disc_size[self.win.
                                                                    units]
        self.calibration_dot_size = self._calibration_dot_size
        self.calibration_disc_size = self._calibration_disc_size
        self.calibration_dot_color = self._calibration_dot_color
        self.calibration_disc_color = self._calibration_disc_color
        self.calibration_target_min = self._calibration_target_min

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
        self.update_calibration = self._update_calibration_auto
        self.gaze_data = []

    def _on_gaze_data(self, gaze_data):
        """Callback function used by Tobii SDK.

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
        # yapf: disable
        if self.embed_event:
            self.datafile.write('\t'.join([
                'TimeStamp',
                'GazePointXLeft',
                'GazePointYLeft',
                'ValidityLeft',
                'GazePointXRight',
                'GazePointYRight',
                'ValidityRight',
                'GazePointX',
                'GazePointY',
                'PupilSizeLeft',
                'PupilValidityLeft',
                'PupilSizeRight',
                'PupilValidityRight',
                'Event'
            ]) + '\n')
        else:
            self.datafile.write('\t'.join([
                'TimeStamp',
                'GazePointXLeft',
                'GazePointYLeft',
                'ValidityLeft',
                'GazePointXRight',
                'GazePointYRight',
                'ValidityRight',
                'GazePointX',
                'GazePointY',
                'PupilSizeLeft',
                'PupilValidityLeft',
                'PupilSizeRight',
                'PupilValidityRight'
            ]) + '\n')
        self._flush_to_file()
        # yapf: enable

    def _write_event(self, record):
        """Write embed events to the data file.

        Args:
            record: reformed gaze data
        Returns:
            None
        """

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
            '%d\t'    # ValidityLeft
            '%.4f\t'  # GazePointXRight
            '%.4f\t'  # GazePointYRight
            '%d\t'    # ValidityRight
            '%.4f\t'  # GazePointX
            '%.4f\t'  # GazePointY
            '%.4f\t'  # PupilSizeLeft
            '%d\t'    # PupilValidityLeft
            '%.4f\t'  # PupilSizeRight
            '%d\t'    # PupilValidityRight
        ) # yapf: disable
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
            if self.embed_event:
                self._write_event(output)
            else:
                self.datafile.write('\n')
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

    def _open_datafile(self):
        """Open a file for gaze data.

        Args:
            None

        Returns:
            None
        """
        try:
            self.close()
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

    def start_recording(self, filename=None, newfile=True, embed_event=False):
        """Start recording

        Args:
            filename: the name of the data file. If None, use default name.
                Defaults to None.
            newfile: open a new file to save data. Defaults to True.
            embed_event: should the file contains the event column.
                Defaults to False.

        Returns:
            None
        """
        if filename is not None:
            if type(filename) == str:
                self.filename = filename
            else:
                raise ValueError('filename should be string')
        if newfile:
            self._open_datafile()

        self.embed_event = embed_event
        self.gaze_data = []
        self.event_data = []
        self.eyetracker.subscribe_to(
            tr.EYETRACKER_GAZE_DATA, self._on_gaze_data, as_dictionary=True)
        core.wait(0.5)  # wait a bit for the eye tracker to get ready
        self.t0 = tr.get_system_time_stamp()
        self.recording = True

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

    def get_current_gaze_position(self):
        """Get the newest gaze position.

        Args:
            None

        Returns:
            (x, y)
        """

        if not self.gaze_data:
            return (np.nan, np.nan)
        else:
            lxy = (np.nan, np.nan)
            rxy = (np.nan, np.nan)
            gaze_data = self.gaze_data[-1]
            if gaze_data['left_gaze_point_validity']:
                lxy = self._get_psychopy_pos(
                    gaze_data['left_gaze_point_on_display_area'])
            if gaze_data['right_gaze_point_validity']:
                rxy = self._get_psychopy_pos(
                    gaze_data['right_gaze_point_on_display_area'])

            if (np.nan not in lxy) and (np.nan not in rxy):
                ave = ((lxy[0]+rxy[0])/2, (lxy[1]+rxy[1])/2)
            elif np.nan not in lxy:
                ave = lxy
            elif np.nan not in rxy:
                ave = rxy
            else:
                ave = (np.nan, np.nan)

            return ave

    def get_current_pupil_size(self):
        """Get the newest pupil size.

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
            if gaze_data['left_pupil_validity']:
                lp = gaze_data['left_pupil_diameter']
            if gaze_data['right_pupil_validity']:
                rp = gaze_data['right_pupil_diameter']

            return (lp, rp)

    def record_event(self, event):
        """Record events with timestamp.

            This method works only during recording.

        Args:
            event: the event

        Returns:
            None
        """
        if not self.recording:
            return

        self.event_data.append([tr.get_system_time_stamp(), event])

    def close(self):
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

    def run_calibration(self, calibration_points, decision_key='space'):
        """Run calibration

        Args:
            calibration_points: list of position of the calibration points.
            decision_key: the key to leave the procedure.

        Returns:
            bool: The status of calibration. True for success, False otherwise.
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
        self.calibration_target_dot = visual.Circle(
            self.win,
            radius=self.calibration_dot_size,
            fillColor=self.calibration_dot_color,
            lineColor=self.calibration_dot_color)
        self.calibration_target_disc = visual.Circle(
            self.win,
            radius=self.calibration_disc_size,
            fillColor=self.calibration_disc_color,
            lineColor=self.calibration_disc_color)
        self.retry_marker = visual.Circle(
            self.win,
            radius=self.calibration_dot_size,
            fillColor=self.calibration_dot_color,
            lineColor=self.calibration_disc_color,
            autoLog=False)
        if self.win.units == 'norm':  # fix oval
            self.calibration_target_dot.setSize(
                [float(self.win.size[1]) / self.win.size[0], 1.0])
            self.calibration_target_disc.setSize(
                [float(self.win.size[1]) / self.win.size[0], 1.0])
            self.retry_marker.setSize(
                [float(self.win.size[1]) / self.win.size[0], 1.0])
        result_msg = visual.TextStim(
            self.win,
            pos=(0, -self.win.size[1] / 4),
            color='white',
            units='pix',
            autoLog=False)

        self.calibration.enter_calibration_mode()

        self.original_calibration_points = calibration_points[:]
        # set all points
        cp_num = len(self.original_calibration_points)
        self.retry_points = list(range(cp_num))

        in_calibration_loop = True
        event.clearEvents()
        while in_calibration_loop:
            self.calibration_points = [
                self.original_calibration_points[x] for x in self.retry_points
            ]

            # clear the display
            self.win.flip()
            self.update_calibration()
            self.calibration_result = self.calibration.compute_and_apply()
            self.win.flip()

            result_img = self._show_calibration_result()
            result_msg.setText(
                'Accept/Retry: {k}\n'
                'Select/Deselect all points: 0\n'
                'Select/Deselect recalibration points: 1-{p} key\n'
                'Abort: esc'.format(k=decision_key, p=cp_num))

            waitkey = True
            self.retry_points = []
            while waitkey:
                for key in event.getKeys():
                    if key in [decision_key, 'escape']:
                        waitkey = False
                    elif key in self.numkey_dict:
                        if key in ["0", 'num_0']:
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
                        self.retry_marker.setPos(
                            self.original_calibration_points[retry_p])
                        self.retry_marker.draw()

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

        self.calibration.leave_calibration_mode()

        return retval

    def _show_calibration_result(self):
        img = Image.new('RGBA', tuple(self.win.size))
        img_draw = ImageDraw.Draw(img)
        result_img = visual.SimpleImageStim(self.win, img, autoLog=False)
        img_draw.rectangle(((0, 0), tuple(self.win.size)),
                            fill=(0, 0, 0, 0))
        if self.calibration_result.status == tr.CALIBRATION_STATUS_FAILURE:
            #computeCalibration failed.
            pass
        else:
            if len(self.calibration_result.calibration_points) == 0:
                pass
            else:
                for calibration_point in self.calibration_result.calibration_points:
                    p = calibration_point.position_on_display_area
                    for calibration_sample in calibration_point.calibration_samples:
                        lp = calibration_sample.left_eye.position_on_display_area
                        rp = calibration_sample.right_eye.position_on_display_area
                        if calibration_sample.left_eye.validity == tr.VALIDITY_VALID_AND_USED:
                            img_draw.line(((p[0] * self.win.size[0],
                                            p[1] * self.win.size[1]),
                                            (lp[0] * self.win.size[0],
                                            lp[1] * self.win.size[1])),
                                            fill=(0, 255, 0, 255))
                        if calibration_sample.right_eye.validity == tr.VALIDITY_VALID_AND_USED:
                            img_draw.line(((p[0] * self.win.size[0],
                                            p[1] * self.win.size[1]),
                                            (rp[0] * self.win.size[0],
                                            rp[1] * self.win.size[1])),
                                            fill=(255, 0, 0, 255))
                    img_draw.ellipse(((p[0] * self.win.size[0] - 3,
                                        p[1] * self.win.size[1] - 3),
                                        (p[0] * self.win.size[0] + 3,
                                        p[1] * self.win.size[1] + 3)),
                                        outline=(0, 0, 0, 255))

        result_img.setImage(img)
        return result_img


    def _update_calibration_auto(self):
        # start calibration
        event.clearEvents()
        clock = core.Clock()
        for current_point_index in self.retry_points:
            self.calibration_target_disc.setPos(
                self.original_calibration_points[current_point_index])
            self.calibration_target_dot.setPos(
                self.original_calibration_points[current_point_index])
            clock.reset()
            while True:
                t = clock.getTime() * self.shrink_speed
                self.calibration_target_disc.setRadius(
                    [(np.sin(t)**2 + self.calibration_target_min) * self.calibration_disc_size])
                self.calibration_target_dot.setRadius(
                    [(np.sin(t)**2 + self.calibration_target_min) * self.calibration_dot_size])
                self.calibration_target_disc.draw()
                self.calibration_target_dot.draw()
                if clock.getTime() >= self._shrink_sec:
                    core.wait(0.5)
                    self._collect_calibration_data(
                        self.original_calibration_points[current_point_index])
                    break

                self.win.flip()

    def show_status(self):
        """Simple procedure to adjust the participant's position.

            This is a modification of show_status in psychopy_tobii_controller.

        Args:
            None

        Returns:
            None
        """

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

        self.eyetracker.subscribe_to(
            tr.EYETRACKER_GAZE_DATA, self._on_gaze_data, as_dictionary=True)
        core.wait(0.5)  # wait a bit for the eye tracker to get ready

        b_show_status = True

        while b_show_status:
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
                lx, ly = self._get_psychopy_pos_from_trackbox([lx, ly],
                                                              units='height')
                leye.setPos((lx * 0.25, ly * 0.2 + 0.4))
                leye.draw()
            if rv:
                rx, ry = self._get_psychopy_pos_from_trackbox([rx, ry],
                                                              units='height')
                reye.setPos((rx * 0.25, ry * 0.2 + 0.4))
                reye.draw()
            if lv or rv:
                zpos.setPos(((((lz * int(lv) + rz * int(rv)) /
                               (int(lv) + int(rv))) - 0.5) * 0.125, 0.28))
                zpos.draw()

            for key in event.getKeys():
                if key == 'space':
                    b_show_status = False
                    break

            self.win.flip()

        self.eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA)

    # property getters and setters for parameter changes
    @property
    def shrink_speed(self):
        return self._shrink_speed

    @shrink_speed.setter
    def shrink_speed(self, value):
        self._shrink_speed = value
        # adjust the duration of shrinking
        self._shrink_sec = 3 / self._shrink_speed

    @property
    def calibration_dot_size(self):
        return self._calibration_dot_size

    @calibration_dot_size.setter
    def calibration_dot_size(self, value):
        self._calibration_dot_size = value

    @property
    def calibration_dot_color(self):
        return self._calibration_dot_color

    @calibration_dot_color.setter
    def calibration_dot_color(self, value):
        self._calibration_dot_color = value

    @property
    def calibration_disc_size(self):
        return self._calibration_disc_size

    @calibration_disc_size.setter
    def calibration_disc_size(self, value):
        self._calibration_disc_size = value

    @property
    def calibration_disc_color(self):
        return self._calibration_disc_color

    @calibration_disc_color.setter
    def calibration_disc_color(self, value):
        self._calibration_disc_color = value

    @property
    def calibration_target_min(self):
        return self._calibration_target_min

    @calibration_target_min.setter
    def calibration_target_min(self, value):
        self._calibration_target_min = value

    @property
    def numkey_dict(self):
        return self._numkey_dict

    @numkey_dict.setter
    def numkey_dict(self, value):
        self._numkey_dict = value

    @property
    def update_calibration(self):
        return self._update_calibration

    @update_calibration.setter
    def update_calibration(self, value):
        self._update_calibration = value


class infant_tobii_controller(tobii_controller):
    def __init__(self, win, id=0, filename='gaze_TOBII_output.tsv'):
        """Tobii controller for PsychoPy.

            tobii_research are required for this module.

        Args:
            win: psychopy.visual.Window object.
            id: the id of eyetracker.
            filename: the name of the data file.

        Attributes:
            shrink_speed: the shrinking speed of target in calibration.
                Defaults to 1.
            numkey_dict: keys used for calibration. Defaults to the number pad.
        """
        super().__init__(win, id, filename)
        self.update_calibration = self._update_calibration_infant
        # slower for infants
        self.shrink_speed = 1

    def _update_calibration_infant(self,
                                   collect_key='space',
                                   exit_key='return'):
        """The calibration procedure designed for infants.

            An implementation of run_calibration() in psychopy_tobii_controller.

        Args:
            collect_key: the key to start collecting samples. Defaults to space.
            exit_key: the key to finish and leave the current calibration
                procedure. It should not be confused with `decision_key`, which
                is used to leave the whole calibration process. `exit_key` is
                used to leave the current calibration, the user may recalibrate
                or accept the results afterwards. Defaults to return (Enter)

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
                    # allow the participant to focus
                    core.wait(0.5)
                    # collect samples when space is pressed
                    if current_point_index in self.retry_points:
                        self._collect_calibration_data(
                            self.
                            original_calibration_points[current_point_index])
                        current_point_index = -1
                elif key == exit_key:
                    # exit calibration when return is presssed
                    in_calibration = False
                    break

            # draw calibration target
            if current_point_index in self.retry_points:
                self.targets[current_point_index].setPos(
                    self.original_calibration_points[current_point_index])
                t = clock.getTime() * self.shrink_speed
                newsize = [(np.sin(t)**2 + self.calibration_target_min) * e
                           for e in self.target_original_size]
                self.targets[current_point_index].setSize(newsize)
                self.targets[current_point_index].draw()
            self.win.flip()

    def run_calibration(self,
                        calibration_points,
                        infant_stims,
                        decision_key='space'):
        """Run calibration

            How to use:
                - Use 1~9 to present calibration stimulus and 0 to hide the target.
                - Press space to start collect calibration samples.
                - Press return (Enter) to finish the calibration and show the result.
                - Choose the points to recalibrate with 1~9.
                - Press decision_key to accept the calibration or recalibrate.

            The experimenter should manually show the stimulus and collect data
            when the subject is paying attention to the stimulus.

        Args:
            calibration_points: list of position of the calibration points.
            infant_stims: list of images to attract the infant.
            decision_key: the key to leave the procedure.

        Returns:
            bool: The status of calibration. True for success, False otherwise.
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
        try:
            self.targets = [
                visual.ImageStim(self.win, image=v, autoLog=False)
                for v in infant_stims
            ]
        except:
            raise RuntimeError(
                'Unable to load the calibration images.\n'
                'Is the number of images equal to the number of calibration points?'
            )
        self.target_original_size = self.targets[0].size
        self.retry_marker = visual.Circle(
            self.win,
            radius=self.calibration_dot_size,
            fillColor=self.calibration_dot_color,
            lineColor=self.calibration_disc_color,
            autoLog=False)
        if self.win.units == 'norm':  # fix oval
            self.retry_marker.setSize(
                [float(self.win.size[1]) / self.win.size[0], 1.0])
        result_msg = visual.TextStim(
            self.win,
            pos=(0, -self.win.size[1] / 4),
            color='white',
            units='pix',
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

            # clear the display
            self.win.flip()
            self.update_calibration()
            self.calibration_result = self.calibration.compute_and_apply()
            self.win.flip()

            result_img = self._show_calibration_result()
            result_msg.setText(
                'Accept/Retry: {k}\n'
                'Select/Deselect all points: 0\n'
                'Select/Deselect recalibration points: 1-{p} key\n'
                'Abort: esc'.format(k=decision_key, p=cp_num))

            waitkey = True
            self.retry_points = []
            while waitkey:
                for key in event.getKeys():
                    if key in [decision_key, 'escape']:
                        waitkey = False
                    elif key in self.numkey_dict:
                        if key in ["0", 'num_0']:
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
                        self.retry_marker.setPos(
                            self.original_calibration_points[retry_p])
                        self.retry_marker.draw()

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

        self.calibration.leave_calibration_mode()

        return retval

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
            lt (float): The looking time in the trial.
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
