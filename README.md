# psychopy_tobii_infant

Create infant-friendly eyetracking experiments with PsychoPy and Tobii eyetrackers.

## What it's for

This package was based on [psychopy_tobii_controller](https://github.com/hsogo/psychopy_tobii_controller), with some some modifications for developmental research.

### Cautions

- This project is unofficial.
- This project is under development.
- Test the scripts thoroughly before jump into data collection!

### TODO

- Support PsychoPy 3
- Support Builder

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
- [psychopy_tobii_controller](https://github.com/hsogo/psychopy_tobii_controller) by Hiroyuki Sogo

## Releases

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
