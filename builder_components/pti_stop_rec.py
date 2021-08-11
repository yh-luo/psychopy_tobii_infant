from psychopy.experiment.components import BaseComponent, Param


class PTIStopRecordingComponent(BaseComponent):
    """Stop collecting eye-tracking data."""
    categories = ["Eyetracking"]
    targets = ["PsychoPy"]

    def __init__(self, exp, parentName, name="pti_stop_rec"):
        super().__init__(exp, parentName, name)
        self.type = "PTIStopRecording"
        self.url = "https://github.com/yh-luo/psychopy_tobii_infant"

        # trim some params:
        for p in ("startType", "startVal", "startEstim", "stopVal", "stopType",
                  "durationEstim", "saveStartStop", "syncScreenRefresh"):
            if p in self.params:
                del self.params[p]

    def writeRoutineStartCode(self, buff):
        code = "tobii_controller.stop_recording()\n"
        buff.writeIndented(code)
