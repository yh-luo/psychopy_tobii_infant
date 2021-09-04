# psychopy_tobii_infant

Create infant-friendly eyetracking experiments with PsychoPy and Tobii eyetrackers.

## What it's for

This package was based on [psychopy_tobii_controller](https://github.com/hsogo/psychopy_tobii_controller), with some some improvements and modifications for developmental research.

## Cautions

- This project is not a stand-alone program. It is an implementation of PsychoPy for Tobii eye trackers.
- This project is unofficial.
- Test the scripts thoroughly before jumping into data collection!

## Author

Yu-Han Luo

## Installation

1. Clone or download this folder
2. Install the package with `pip install .` or put the folder in your project

## Basic usage

```python
import os
from psychopy import visual, core

from psychopy_tobii_infant import TobiiInfantController

# create a Window to control the monitor
win = visual.Window(
    size=[1280, 1024],
    units='norm',
    fullscr=True,
    allowGUI=False)
# initialize TobiiInfantController to communicate with the eyetracker
controller = TobiiInfantController(win)

# show the relative position of the subject to the eyetracker
# Press space to exit
controller.show_status()

# run calibration
# - Use 1~9 (depending on the number of calibration points) to present
#   calibration stimulus and 0 to hide the target.
# - Press space to start collect calibration samples.
# - Press return (Enter) to finish the calibration and show the result.
# - Choose the points to recalibrate with 1~9.
# - Press decision_key (default to Space) to accept the calibration or recalibrate.
# stimuli to use in calibration
# The number of stimuli must be the same or larger than the calibration points.

# stimuli for calibration
CALISTIMS = [x for x in os.listdir('infant/') if '.png' in x]
# correct path for calibration stimuli
CALISTIMS = ['infant/{}'.format(x) for x in CALISTIMS]
controller.run_calibration([(-0.4, 0.4), (-0.4, -0.4), (0.0, 0.0), (0.4, 0.4), (0.4, -0.4)], CALISTIMS)

# Start recording
controller.start_recording('demo1-test.tsv')
core.wait(3) # record for 3 seconds

# stop recording
controller.stop_recording()
# close the file
controller.close()

# shut down the experiment
win.close()
core.quit()
```

## Requirements

### Python 3.5.x or 3.6.x

Currently tested on Python 3.5.7 and Python 3.6.9

### Dependency

- [PsychoPy](http://www.psychopy.org/)
  - supports both PsychoPy2 (tested on 1.90.3, should work on older version) and PsychoPy 3 (tested on 3.2.3)
- [tobii-research](https://pypi.python.org/pypi/tobii-research)
  - `>=1.6.0` for Python 3.5
  - `>=1.7.0` for Python 3.6

#### Optional

- [prosdk-addons-python](https://github.com/tobiipro/prosdk-addons-python)

If you wish to run calibration validation, you need to install or put the add-ons **inside** the source folder:
The add-ons are Apache-2.0 licensed.

```
psychopy_tobii_infant
├── __init__.py
└── tobii_research_addons
    ├── __init__.py
    ├── ScreenBasedCalibrationValidation.py
    └── vectormath.py
```

## Demo

Demo stimuli released under Creative Commons CC0, aka no copyright:
+ [infant/](https://bit.ly/2BnAGwG)
+ [stim/](https://bit.ly/2SQAOf9)

**Notes**

On Windows machines, PsychoPy sometimes is not focused and keyboard inputs are not detected by PsychoPy.
Users might get stuck in `show_status()` or other procedures that require keyboard inputs. Details can be found in [#8](https://github.com/yh-luo/psychopy_tobii_infant/issues/8). Two workarounds are provided:
- Simply put `from moviepy.config import get_setting` in the beginning of the script.
- Use Alt + Tab to manually focus PsychoPy.

### demo1_calibration.py

1. Show the relative position of the subject to the eyetracker
2. Run five-points calibration

### demo2_collect_looking_time.py

1. Show the relative position of the subject to the eyetracker
2. Run five-points calibration
3. Collect looking time data based on the eyetracker (static image)

### demo3_collect_looking_time_with_video.py

1. Show the relative position of the subject to the eyetracker
2. Run five-points calibration
3. Collect looking time data based on the eyetracker (video)

### demo4_generic_controller.py

1. Show the relative position of the subject to the eyetracker
2. Adjust parameters of calibration procedure
3. Run five-points calibration automatically

### demo5_customized_calibration.py

1. Show the relative position of the subject to the eyetracker
2. Use customized calibration procedure to attract the participant's attention
   - visual stimulus shriking and a sound playing during calibration
3. Run five-points calibration

### demo6_calibration_with_sound.py

1. Show the relative position of the subject to the eyetracker
2. Run five-points calibration with sound

### demo7_calibration_validation

1. Show the relative position of the subject to the eyetracker
2. Run five-points calibration automatically
3. Run calibration validation automatically and show the results

## Changelog

### [0.8.0] 2021-9

#### Improvements

+ Validation procedure for `TobiiInfantController`.
+ New `shuffle` argument (default is `True`) for `TobiiInfantController.run_calibration` to control the randomization of calibration stimuli.

#### Changed

+ A large part of codes had been refactored. If you used a modified version of this package, please be aware of that before upgrading!
+ New class `InfantStimuli` are used to handle the images for infant-friendly calibration/validation.
Users now can use additional arguments of `psychopy.visual.ImageStim` for the calibration stimuli.

### [0.7.1] 2021-4

#### Changed

Codes conform to PEP8 now. Class names are backward-compatible so old scripts should run as expected.

+ `tobii_controller` -> `TobiiController`
+ `tobii_infant_controller` -> `TobiiInfantController`

### [0.7.0] 2021-4

#### Improvements

+ Calibration validation provided by Tobii Pro SDK add-ons. 
+ `focus_time` in `tobii_controller.run_calibration` allows the adjustment of duration allowing the subject to focus.

### [0.6.1] 2020-3

#### Improvements

+ Data precision was slightly improved.
+ Code readability was improved.

#### Changed

+ `tobii_controller.get_current_pupil_size` now returns the average pupil size from both eyes instead of respective values.

#### Removed

- `tobii_controller._write_header` was no longer used. Will only affect users if it is used in the scripts.

### [0.6.0] 2019-10

#### Improvements

+ Python 3.6 support
  + `tobii-research`, started from v1.7, now supports Python 3.6 (yay!).

### [0.5.0] 2019-10

#### Added

- `audio` parameter in `psychopy_tobii_infant.infant_tobii_controller.run_calibration()`. Users can provide a psychopy.sound.Sound object to play during calibration.

#### Removed

- Redundant property getters and setters. Do not affect users.
- Remove `embed_event`. The output file will always record the events in the end of data. Will only affect users if `embed_event` is used in the scripts.

## License

GPL v3.0 or later

## Acknowledgments

This package is built upon/inspired by the following packages, for which credit goes out to the respective authors.

- [PsychoPy](http://www.psychopy.org/)
- [Tobii Pro SDK](https://www.tobiipro.com/product-listing/tobii-pro-sdk/)
- [Tobii Pro SDK add-ons](https://github.com/tobiipro/prosdk-addons-python), Apache-2.0 licensed
- [psychopy_tobii_controller](https://github.com/hsogo/psychopy_tobii_controller) by [Hiroyuki Sogo](https://github.com/hsogo)
- [PyGaze](http://www.pygaze.org/) by [Edwin S. Dalmaijer](https://github.com/esdalmaijer)

## Citation

Please consider to cite PsychoPy to encourage open-source projects:

(APA formatted)
- Peirce, J. (2009). Generating stimuli for neuroscience using PsychoPy. Frontiers in Neuroinformatics, 2, 10. doi:10.3389/neuro.11.010.2008
