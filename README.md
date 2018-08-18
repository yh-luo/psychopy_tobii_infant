# psychopy_tobii_infant

Create infant-friendly eyetracking experiments with PsychoPy and psychopy_tobii_controller.

## Who it's for

This package was mostly based on [psychopy_tobii_controller](https://github.com/hsogo/psychopy_tobii_controller), with some some modifications to make life easier for anyone who works with infants and children.

### Cautions

- This project is unofficial.
- This project is under development.
- Test the scripts thoroughly before jumping into data collection!

### TODO

- Support PsychoPy 3
- Support Builder
- Add documentations

## Author

Yu-Han Luo

## Installation

### Use git

1. Clone this folder
    ```bash
    git clone https://github.com/yh-luo/psychopy_tobii_infant.git
    ```
2. Navigate to the folder
3. install the package with `pip`
    ```python
    pip install .
    ```

### Download the ZIP file

1. Download this folder (the green button)
2. Unzip the file and navigate to the folder
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

**v0.1**: released on GitHub, 2018/08/18

## Examples

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
