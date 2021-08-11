from psychopy.experiment.components import BaseComponent, Param


class PTIEventComponent(BaseComponent):
    """Record events with timestamp."""
    categories = ["Eyetracking"]
    targets = ["PsychoPy"]

    def __init__(self,
                 exp,
                 parentName,
                 name="pti_event",
                 message="u'event_marker'",
                 syncScreenRefresh=True):
        super().__init__(exp,
                         parentName,
                         name,
                         syncScreenRefresh=syncScreenRefresh)
        self.type = "PTIEvent"
        self.url = "https://github.com/yh-luo/psychopy_tobii_infant"

        self.params["message"] = Param(message,
                                       valType="code",
                                       updates="constant",
                                       hint="What to write to the file",
                                       label="Message")

        # trim some params:
        for p in ("startType", "startVal", "startEstim", "stopVal", "stopType",
                  "durationEstim", "saveStartStop"):
            if p in self.params:
                del self.params[p]

    def writeRoutineStartCode(self, buff):
        code = "%(name)s_sent = False\n"
        buff.writeIndented(code % self.params)

    def writeFrameCode(self, buff):
        code = "if not %(name)s_sent:\n"
        buff.writeIndented(code % self.params)
        buff.setIndentLevel(1, relative=True)
        if self.params['syncScreenRefresh'].val:
            code = (
                "win.callOnFlip(tobii_controller.record_event, %(message)s)\n"
                "%(name)s_sent = True\n")
        else:
            code = ("tobii_controller.record_event(%(message)s)\n"
                    "%(name)s_sent = True\n")
        buff.writeIndentedLines(code % self.params)
        buff.setIndentLevel(-1, relative=True)
