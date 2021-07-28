from psychopy.experiment.components import BaseComponent, Param


class EyetrackerValidComponent(BaseComponent):
    """Run validation."""
    categories = ["Eyetracking"]
    targets = ["PsychoPy"]

    def __init__(self,
                 exp,
                 parentName,
                 name="eyetracker_valid",
                 validation_points=None,
                 sample_count=30,
                 timeout=1,
                 focus_time=0.5,
                 decision_key="space",
                 show_results=False,
                 save_to_file=True):
        super().__init__(exp, parentName, name)
        self.type = "EyetrackerValid"
        self.url = "https://github.com/yh-luo/psychopy_tobii_infant"

        self.params["validation_points"] = Param(
            validation_points,
            valType="code",
            updates="constant",
            hint=
            "List of validation points. None to use the calibration points",
            label="Validation points")
        self.params["sample_count"] = Param(
            sample_count,
            valType="code",
            updates="constant",
            hint="Default is 30, minimum 10, maximum 3000",
            label="The number of samples to collect")
        self.params["timeout"] = Param(
            timeout,
            valType="code",
            updates="constant",
            hint="Default is 1, minimum 0.1, maximum 3",
            label="Timeout in seconds")
        self.params["focus_time"] = Param(
            focus_time,
            valType="code",
            updates="constant",
            hint="The duration allowing the subject to focus in seconds",
            label="Focus time")
        self.params["decision_key"] = Param(decision_key,
                                            valType="str",
                                            updates="constant",
                                            hint="key to leave the procedure",
                                            label="Decision key",
                                            categ="Advanced")
        self.params["show_results"] = Param(show_results,
                                            valType="bool",
                                            updates="constant",
                                            label="Show validation results",
                                            categ="Advanced")
        self.params["save_to_file"] = Param(
            save_to_file,
            valType="bool",
            updates="constant",
            label="Save validation results to the file",
            categ="Advanced")

    def writeRoutineStartCode(self, buff):

        code = "tobii_controller.run_validation(\n"
        buff.writeIndented(code % self.params)
        buff.setIndentLevel(1, relative=True)
        code = (
            "validation_points=%(validation_points)s,\n"
            "sample_count=%(sample_count)s,\n"
            "timeout=%(timeout)s,\n"
            "focus_time=%(focus_time)s,\n"
            "decision_key=%(decision_key)s,\n"
            "show_results=%(show_results)s,\n"
            "save_to_file=%(save_to_file)s"
        )
        buff.writeIndentedLines(code % self.params)
        buff.setIndentLevel(-1, relative=True)
        code = ")\n"
        buff.writeIndented(code % self.params)

    def writeFrameCode(self, buff):
        pass

    def writeRoutineEndCode(self, buff):
        pass
