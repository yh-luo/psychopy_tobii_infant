from psychopy.experiment.components import BaseComponent, Param


class EyetrackerEventComponent(BaseComponent):
    """Record events with timestamp."""
    categories = ["Eyetracking"]
    targets = ["PsychoPy"]

    def __init__(self,
                 exp,
                 parentName,
                 name="eyetacker_event",
                 message="event_marker",
                 syncScreenRefresh=True):
        super().__init__(exp, parentName, name)
        self.type = "EyetrackerEvent"
        self.url = "https://github.com/yh-luo/psychopy_tobii_infant"

        self.params["message"] = Param(message,
                                       valType="str",
                                       updates="constant",
                                       hint="What to write to the file",
                                       label="Message")

    def writeRoutineStartCode(self, buff):
        code = "%(name)s_sent = False\n"
        buff.writeIndented(code % self.params)

    def writeFrameCode(self, buff):
        code = "if not %(name)s_sent:\n"
        buff.writeIndented(code % self.params)
        buff.setIndentLevel(1, relative=True)
        code = ("tobii_controller.record_event(%(message)s)\n"
                "%(name)s_sent = True\n")
        buff.writeIndentedLines(code % self.params)
        buff.setIndentLevel(-1, relative=True)

    def writeRoutineEndCode(self, buff):
        pass
