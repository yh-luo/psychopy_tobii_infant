from psychopy.experiment.components import BaseComponent, Param


class EyetrackerRecComponent(BaseComponent):
    """Collect eye-tracking data in a routine."""
    categories = ["Eyetracking"]
    targets = ["PsychoPy"]

    def __init__(self,
                 exp,
                 parentName,
                 name="eyetacker_rec",
                 file_suffix="_TOBII.tsv",
                 newfile=True):
        super().__init__(exp, parentName, name)
        self.type = "EyetrackerRec"
        self.url = "https://github.com/yh-luo/psychopy_tobii_infant"

        self.params["file_suffix"] = Param(file_suffix,
                                           valType="str",
                                           updates="constant",
                                           label="Suffix of the data file")
        msg = ("Whether to write the data to a new file."
               "file_suffix has no effects if newfile=False")
        self.params["newfile"] = Param(newfile,
                                       valType="bool",
                                       updates="constant",
                                       hint=msg,
                                       label="Open a new file",
                                       categ="Advanced")

    def writeRoutineStartCode(self, buff):
        if self.params["newfile"].val:
            code = ("tobii_controller.start_recording(filename="
                    "filename + %(file_suffix)s)\n")
        else:
            code = "tobii_controller.start_recording(newfile=False)\n"
        buff.writeIndented(code % self.params)

    def writeFrameCode(self, buff):
        pass

    def writeRoutineEndCode(self, buff):
        code = "tobii_controller.stop_recording()\n"
        buff.writeIndented(code % self.params)
