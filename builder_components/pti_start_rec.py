from psychopy.experiment.components import BaseComponent, Param


class PTIStartRecordingComponent(BaseComponent):
    """Start collecting eye-tracking data."""
    categories = ["Eyetracking"]
    targets = ["PsychoPy"]

    def __init__(self,
                 exp,
                 parentName,
                 name="pti_start_rec",
                 tobii_filename=(
                     "u'data/%s_%s_%s_TOBII.tsv'"
                     "% (expInfo['participant'], expName, expInfo['date'])"),
                 newfile=True):
        super().__init__(exp, parentName, name)
        self.type = "PTIStartRecording"
        self.url = "https://github.com/yh-luo/psychopy_tobii_infant"

        self.params["tobii_filename"] = Param(
            tobii_filename,
            valType="code",
            updates="constant",
            label="Filename of the Tobii output")
        self.params["newfile"] = Param(
            newfile,
            valType="bool",
            updates="constant",
            hint=("Whether to write the data to a new file."
                  "tobii_filename has no effects if newfile=False"),
            label="Open a new file",
            categ="Advanced")

        # trim some params:
        for p in ("startType", "startVal", "startEstim", "stopVal", "stopType",
                  "durationEstim", "saveStartStop", "syncScreenRefresh"):
            if p in self.params:
                del self.params[p]

    def writeRoutineStartCode(self, buff):
        if self.params["newfile"].val:
            code = "tobii_controller.start_recording(%(tobii_filename)s)\n"
        else:
            code = "tobii_controller.start_recording(newfile=False)\n"
        buff.writeIndented(code % self.params)
