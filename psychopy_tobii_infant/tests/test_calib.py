from psychopy import monitors, visual
from psychopy_tobii_infant import TobiiController


class DummyCalibration:
    def __init__(self):
        pass

    def enter_calibration_mode(self):
        pass

    def leave_calibration_mode(self):
        pass

    def collect_data(self, *args):
        pass

    def discard_data(self):
        pass

    def compute_and_apply(self):
        # Returns A CalibrationResult object.
        return DummyCalibrationResult()


class DummyCalibrationResult:
    def __init__(self):
        self.status = "calibration_status_failure"
        self.calibration_points = []


class DummyController(TobiiController):
    def __init__(self, win):
        self.win = win
        self.numkey_dict = self._default_numkey_dict
        self.calibration_dot_size = self._default_calibration_dot_size[
            self.win.units]
        self.calibration_disc_size = self._default_calibration_disc_size[
            self.win.units]
        self.eyetracker = -1  # None will raise exceptions
        self.calibration = DummyCalibration()
        self.update_calibration = self._update_calibration_auto


class TestCalib:
    """Test the presentation of calibration results."""
    def setup(self):
        self.mon = monitors.Monitor("dummy",
                                    width=12.8,
                                    distance=65,
                                    autoLog=False)
        self.win = visual.Window(size=[128, 128],
                                 units="norm",
                                 monitor=self.mon,
                                 fullscr=False,
                                 allowGUI=False,
                                 autoLog=False)

        self.controller = DummyController(self.win)

    def test_calibration(self):
        cal_points = [(-0.4, 0.4), (-0.4, -0.4), (0.0, 0.0), (0.4, 0.4),
                      (0.4, -0.4)]
        self.controller.run_calibration(cal_points,
                                        focus_time=0.2,
                                        result_msg_color="black")

    def test_validation(self):
        pass
