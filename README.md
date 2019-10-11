# psychopy_tobii_infant

Create infant-friendly eyetracking experiments with PsychoPy and Tobii eyetrackers.

## What it's for

This package was based on [psychopy_tobii_controller](https://github.com/hsogo/psychopy_tobii_controller), with some some modifications for developmental research.

## Cautions

- This project is not a stand-alone program. It is an implementation of PsychoPy for Tobii eye trackers.
- This project is unofficial and under development.
- Test the scripts thoroughly before jumping into data collection!

## Author

Yu-Han Luo

## Installation

1. Clone or download this folder
2. Install the package with `pip install .` or put the folder in your project


## Basic usage

```python
import os
from psychopy import visual, event, core

from psychopy_tobii_infant import infant_tobii_controller

# create a Window to control the monitor
win = visual.Window(
    size=[1280, 1024],
    units='norm',
    fullscr=True,
    allowGUI=False)
# initialize tobii_controller to communicate with the eyetracker
controller = infant_tobii_controller(win)

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
core.quit()
```

+ Demo stimuli released under Creative Commons CC0, aka no copyright:
  + [infant/](https://bit.ly/2BnAGwG)
  + [stim/](https://bit.ly/2SQAOf9)

## Requirements

### Python 3.5.x

Currently tested on Python 3.5.6

### Dependency

- [PsychoPy 1.90.3](http://www.psychopy.org/)
- [tobii_research](https://pypi.python.org/pypi/tobii-research)

## Demo

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
2. Adjust parameters of calibration stimuli
3. Run five-points calibration automatically


### demo5_customized_calibration.py

1. Show the relative position of the subject to the eyetracker
2. Use customized calibration procedure to attract the participant's attention
   - visual stimulus shriking and a sound playing during calibration
3. Run five-points calibration

## License

GPL v3.0 or later

## Acknowledgments

This package is built upon/inspired by the following packages, for which credit goes out to the respective authors.

- [PsychoPy](http://www.psychopy.org/)
- [Tobii Pro SDK](https://www.tobiipro.com/product-listing/tobii-pro-sdk/)
- [psychopy_tobii_controller](https://github.com/hsogo/psychopy_tobii_controller) by [Hiroyuki Sogo](https://github.com/hsogo)
- [PyGaze](http://www.pygaze.org/) by [Edwin S. Dalmaijer](https://github.com/esdalmaijer)

## Citation

Please consider to cite PsychoPy to encourage open-source projects:

(APA formatted)
- Peirce, J. (2009). Generating stimuli for neuroscience using PsychoPy. Frontiers in Neuroinformatics, 2, 10. doi:10.3389/neuro.11.010.2008
