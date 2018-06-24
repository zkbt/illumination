from playground.imports import *
from playground.tv.frames import *
from playground.cartoons import *
from playground.tv.animation import animate


'''
These shouldn't work yet, because we haven't clearly set up
how to create an illustration if all you've made is a frame.

directory = 'examples/'
mkdir(directory)
def test_imshow():
    print("\nTesting an imshow Frame.")
    frame = imshowFrame(data=[create_test_fits(rows=300, cols=300) for _ in range(10)], ext_image=1)
    frame.plot()
    filename = os.path.join(directory, 'frame-imshow-animation.mp4')
    animate(frame, filename)
    print("Take a look at {} and see what you think!".format(filename))
    return frame

def test_CameraFrame():
    print("\nTesting an Camera Frame.")
    frame = CameraFrame(data=[create_test_fits(rows=300, cols=300) for _ in range(10)], ext_image=1)
    frame.plot()
    filename = os.path.join(directory, 'frame-camera-animation.mp4')
    animate(frame, filename)
    print("Take a look at {} and see what you think!".format(filename))
    return frame
'''
