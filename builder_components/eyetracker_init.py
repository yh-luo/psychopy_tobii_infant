from psychopy.experiment.components import BaseComponent, Param


class EyetrackerInitComponent(BaseComponent):
    """Initialize the controller instance."""
    categories = ["Eyetracking"]
    targets = ["PsychoPy"]

    def __init__(self,
                 exp,
                 parentName,
                 name="eyetracker_init",
                 id=0,
                 infant=True):
        super().__init__(exp, parentName, name)
        self.type = "EyetrackerInit"
        self.url = "https://github.com/yh-luo/psychopy_tobii_infant"

        self.order = ["name", "id", "infant"]
        self.params["id"] = Param(
            id,
            valType="code",
            updates="constant",
            hint="ID of the eyetracker (0 if the first found eyetracker)",
            label="Tobii eyetracker ID")
        self.params["infant"] = Param(
            infant,
            valType="bool",
            inputType="bool",
            hint="Use the default infant-friendly calibration procedure",
            label="Infant-friendly calibration")

    def writeInitCode(self, buff):
        if self.params["infant"].val:
            code = (
                "from psychopy_tobii_infant import TobiiInfantController\n"
                "tobii_controller = TobiiInfantController(win, id=%(id)s)\n")
        else:
            code = ("from psychopy_tobii_infant import TobiiController\n"
                    "tobii_controller = TobiiController(win, id=%(id)s)\n")

        buff.writeIndentedLines(code % self.params)

    def writeFrameCode(self, buff):
        pass

    def writeExperimentEndCode(self, buff):
        buff.writeIndented("tobii_controller.close()\n")
