# psychopy_tobii_infant

Create infant-friendly eyetracking experiments with PsychoPy and Tobii eyetrackers.

## What it's for

This package was based on [psychopy_tobii_controller](https://github.com/hsogo/psychopy_tobii_controller), with some some modifications for developmental research.

## Cautions

- This project is not a stand-alone program. It is an implementation of PsychoPy for Tobii eye trackers.
- This project is unofficial and under development.
- Test the scripts thoroughly before jump into data collection!

## Author

Yu-Han Luo

## Installation

1. Clone or download this folder
2. Navigate to the folder
3. Install the package with `pip`
    ```python
    pip install .
    ```

## Requirements

### Python 3.5.x

Currently tested on Python 3.5.6

### Dependency

- [PsychoPy 1.90.x](http://www.psychopy.org/)
    Currently tested on v1.90.3
- [tobii_research](https://pypi.python.org/pypi/tobii-research)

## Releases

### v0.4

- Add generic tobii controller, infant_tobii_controller now is a subclass of it.

### v0.3

- Rewrite data collection
- Rewrite data output
- Improve documentation

### v0.2

- Fix the coordinate systems

### v0.1

## Demo

### demo1_calibration.py

1. Show the relative position of the subject to the eyetracker.
2. Run five-points calibration

### demo2_collect_looking_time.py

1. Show the relative position of the subject to the eyetracker.
2. Run five-points calibration
3. Collect looking time data based on the eyetracker (static image)

### demo3_collect_looking_time_with_video.py

1. Show the relative position of the subject to the eyetracker.
2. Run five-points calibration
3. Collect looking time data based on the eyetracker (video)

## License

GPL v3.0 or later

## Acknowledgements

This package is built upon/inspired by the following packages, for which credit goes out to the respective authors.

- [PsychoPy](http://www.psychopy.org/)
- [Tobii Pro SDK](https://www.tobiipro.com/product-listing/tobii-pro-sdk/)
- [psychopy_tobii_controller](https://github.com/hsogo/psychopy_tobii_controller) by [Hiroyuki Sogo](https://github.com/hsogo)
- [PyGaze](http://www.pygaze.org/) by [Edwin S. Dalmaijer](https://github.com/esdalmaijer)

## Citation

At the moment, I do not have a formal publication for it. Since it may hopefully help my academic career (if I have one), please consider to cite both this package and PsychoPy:

(APA formatted)
- Luo, Y.-H. (2018). psychopy_tobii_infant. Retrieved from https://github.com/yh-luo/psychopy_tobii_infant
- Peirce, J. (2009). Generating stimuli for neuroscience using PsychoPy. Frontiers in Neuroinformatics, 2, 10. doi:10.3389/neuro.11.010.2008
