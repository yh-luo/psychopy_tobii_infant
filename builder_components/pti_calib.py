from psychopy.experiment.components import BaseComponent, Param


class PTICalibrationComponent(BaseComponent):
    """Run calibration."""
    categories = ["Eyetracking"]
    targets = ["PsychoPy"]

    def __init__(self,
                 exp,
                 parentName,
                 name="pti_calib",
                 show_status=True,
                 calibration_points=[(-0.4, 0.4), (-0.4, -0.4), (0.0, 0.0),
                                     (0.4, 0.4), (0.4, -0.4)],
                 infant_stims=[
                     "infant/cow.png", "infant/elk.png", "infant/hippo.png",
                     "infant/ladybug.png", "infant/panda.png"
                 ],
                 audio=None,
                 focus_time=0.5,
                 decision_key="space"):
        super().__init__(exp, parentName, name)
        self.type = "PTICalibration"
        self.url = "https://github.com/yh-luo/psychopy_tobii_infant"

        self.params["show_status"] = Param(
            show_status,
            valType="bool",
            updates="constant",
            hint="Show the participant's gaze position in track box",
            label="Show status")
        self.params["calibration_points"] = Param(
            calibration_points,
            valType="code",
            updates="constant",
            hint="List of calibration points",
            label="Calibration points")
        self.params["infant_stims"] = Param(
            infant_stims,
            valType="code",
            updates="constant",
            hint=("List of images to attract the subject. Has no effect if "
                  "'Infant-friendly calibration' is not toggled in pti_init"),
            label="Calibration targets")
        self.params["audio"] = Param(
            audio,
            valType="code",
            updates="constant",
            hint=
            ("Sound object to play during collecting calibration samples. Has "
             "no effect if 'Infant-friendly calibration' is not toggled in "
             "pti_init"),
            label="Sound object for calibration")
        self.params["focus_time"] = Param(
            focus_time,
            valType="code",
            updates="constant",
            hint="The duration allowing the subject to focus in seconds",
            label="Focus time",
            categ="Advanced")
        self.params["decision_key"] = Param(decision_key,
                                            valType="str",
                                            updates="constant",
                                            hint="key to leave the procedure",
                                            label="Decision key",
                                            categ="Advanced")
        # trim some params:
        for p in ("startType", "startVal", "startEstim", "stopVal", "stopType",
                  "durationEstim", "saveStartStop", "syncScreenRefresh"):
            if p in self.params:
                del self.params[p]

    def writeRoutineStartCode(self, buff):
        if self.params["show_status"].val:
            code = ("tobii_controller.show_status("
                    "decision_key=%(decision_key)s)\n")
            buff.writeIndentedLines(code % self.params)
        # check which controller is used
        code = "if controller_infant_mode:\n"
        buff.writeIndented(code)
        buff.setIndentLevel(1, relative=True)
        code = "tobii_controller.run_calibration(\n"
        buff.writeIndented(code)
        buff.setIndentLevel(1, relative=True)
        code = ("calibration_points=%(calibration_points)s,\n"
                "focus_time=%(focus_time)s,\n"
                "decision_key=%(decision_key)s,\n"
                "infant_stims=%(infant_stims)s,\n"
                "audio=%(audio)s)\n")
        buff.writeIndentedLines(code % self.params)
        buff.setIndentLevel(-2, relative=True)
        code = "else:\n"
        buff.writeIndented(code)
        buff.setIndentLevel(1, relative=True)
        code = "tobii_controller.run_calibration(\n"
        buff.writeIndented(code)
        buff.setIndentLevel(1, relative=True)
        code = ("calibration_points=%(calibration_points)s,\n"
                "focus_time=%(focus_time)s,\n"
                "decision_key=%(decision_key)s)\n")
        buff.writeIndentedLines(code % self.params)
        buff.setIndentLevel(-2, relative=True)
