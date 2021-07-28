from psychopy.experiment.components import BaseComponent, Param


class EyetrackerCalibComponent(BaseComponent):
    """Run calibration."""
    categories = ["Eyetracking"]
    targets = ["PsychoPy"]

    def __init__(self,
                 exp,
                 parentName,
                 name="eyetracker_calib",
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
        self.type = "EyetrackerCalib"
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
            hint="List of images to attract the subject",
            label="Calibration targets")
        self.params["audio"] = Param(
            audio,
            valType="code",
            updates="constant",
            hint="Sound object to play during collecting calibration samples",
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

    def writeRoutineStartCode(self, buff):
        if self.params["show_status"].val:
            code = ("tobii_controller.show_status("
                    "decision_key=%(decision_key)s)\n")
            buff.writeIndentedLines(code % self.params)
        code = "tobii_controller.run_calibration(\n"
        buff.writeIndented(code % self.params)
        buff.setIndentLevel(1, relative=True)
        code = ("calibration_points=%(calibration_points)s,\n"
                "infant_stims=%(infant_stims)s,\n"
                "audio=%(audio)s,\n"
                "focus_time=%(focus_time)s,\n"
                "decision_key=%(decision_key)s")
        buff.writeIndentedLines(code % self.params)
        buff.setIndentLevel(-1, relative=True)
        code = ")\n"
        buff.writeIndented(code)

    def writeFrameCode(self, buff):
        pass

    def writeRoutineEndCode(self, buff):
        pass
