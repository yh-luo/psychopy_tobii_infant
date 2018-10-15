import math
from psychopy import visual, event, core, prefs

# create a Window to control the monitor
win = visual.Window(
    size=[1280, 1024],
    screen=1,
    # fullscr=True,
    allowGUI=False,
    units='pix')


# draw the fixation target
def shrinker(t, size, smallest_ratio=0.2):
    return [(math.sin(t)**2 + smallest_ratio) * e for e in size]


# def draw_target(pos, speed=1, sec=3):
#     in_circle = visual.Circle(
#         win, radius=10, units='pix', fillColor=(1, 1, 1), lineColor=(1, 1, 1))
#     out_circle = visual.Circle(
#         win,
#         radius=60,
#         units='pix',
#         fillColor=(-1, -1, -1),
#         lineColor=(-1, -1, -1))

#     out_circle_original = out_circle.size
#     in_circle_original = in_circle.size
#     clock = core.Clock()

#     while clock.getTime() <= sec:
#         t = clock.getTime() * speed
#         out_circle.setPos(pos)
#         in_circle.setPos(pos)
#         out_circle.setSize(shrinker(t, out_circle_original))
#         in_circle.setSize(shrinker(t, in_circle_original))
#         out_circle.draw()
#         in_circle.draw()


numkey_dict = {
    'num_0': -1,
    'num_1': 0,
    'num_2': 1,
    'num_3': 2,
    'num_4': 3,
    'num_5': 4,
    'num_6': 5,
    'num_7': 6,
    'num_8': 7,
    'num_9': 8
}

# define calibration points
DISPSIZE = (1280, 1024)
CALINORMP = [(-0.4, 0.4), (-0.4, -0.4), (0.0, 0.0), (0.4, 0.4), (0.4, -0.4)]
calibration_point = [(x * DISPSIZE[0], y * DISPSIZE[1]) for x, y in CALINORMP]
cp_num = len(calibration_point)
retry_points = list(range(cp_num))

original_calibration_points = calibration_point

in_circle = visual.Circle(
win, radius=10, units='pix', fillColor=(1, 1, 1), lineColor=(1, 1, 1))
out_circle = visual.Circle(
win,
radius=60,
units='pix',
fillColor=(-1, -1, -1),
lineColor=(-1, -1, -1))

out_circle_original = out_circle.size
in_circle_original = in_circle.size
# start calibration
event.clearEvents()
current_point_index = -1
in_calibration = True
clock = core.Clock()
while in_calibration:
    # get keys
    # keys = event.getKeys()
    # for key in keys:
    #     if key in numkey_dict:
    #         current_point_index = numkey_dict[key]
    for point in calibration_point:
        clock.reset()
        # elif key == 'space':
        #     # allow the participant to focus
        #     core.wait(0.5)
        #     # collect samples when space is pressed
        #     if current_point_index in retry_points:
        #     #     self._collect_calibration_data(
        #     #         self.original_calibration_points[
        #     #             current_point_index])
        #         current_point_index = -1
        # elif key == 'return':
        #     # exit calibration when return is presssed
        #     in_calibration = False
        #     break

    # draw calibration target
        while True:
        # if current_point_index in retry_points:
            t = clock.getTime() * 1
            out_circle.setPos(original_calibration_points[calibration_point.index(point)])
            in_circle.setPos(original_calibration_points[calibration_point.index(point)])
            out_circle.setSize(shrinker(t, out_circle_original))
            in_circle.setSize(shrinker(t, in_circle_original))
            out_circle.draw()
            in_circle.draw()
            if t >= 3:
                core.wait(0.5)
                current_point_index = -1
                break

            win.flip()
