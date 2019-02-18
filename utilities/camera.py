# -*- coding: utf-8 -*-
"""

@author: Steinn Ymir Agustsson

    Copyright (C) 2018 Steinn Ymir Agustsson

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import time

import cv2
import numpy as np

from utilities import misc


def prop_id(string=None):
    names = ['CV_CAP_PROP_POS_MSEC', 'CV_CAP_PROP_POS_FRAMES', 'CV_CAP_PROP_POS_AVI_RATIO', 'CV_CAP_PROP_FRAME_WIDTH',
             'CV_CAP_PROP_FRAME_HEIGHT', 'CV_CAP_PROP_FPS', 'CV_CAP_PROP_FOURCC', 'CV_CAP_PROP_FRAME_COUNT',
             'CV_CAP_PROP_FORMAT', 'CV_CAP_PROP_MODE', 'CV_CAP_PROP_BRIGHTNESS', 'CV_CAP_PROP_CONTRAST',
             'CV_CAP_PROP_SATURATION', 'CV_CAP_PROP_HUE', 'CV_CAP_PROP_GAIN', 'CV_CAP_PROP_EXPOSURE',
             'CV_CAP_PROP_CONVERT_RGB', 'CV_CAP_PROP_WHITE_BALANCE', 'CV_CAP_PROP_RECTIFICATION']
    if string == None:
        for i, x in enumerate(names):
            print(i, x)
    for i, x in enumerate(names):
        if string.upper() in x:
            return i


def show_webcam(cam):
    while True:
        r_, img = cam.read()
        cv2.imshow('rgb', img)
        if cv2.waitKey(1) == 27:
            break
    cv2.destroyAllWindows()


class SimCam(object):

    def __init__(self, shape=(600, 800), small_changes=True, force_roundish=True):

        self.lenx, self.leny = shape
        self.x = np.linspace(0, self.lenx - 1, self.lenx)
        self.y = np.linspace(0, self.leny - 1, self.leny)
        self.xx, self.yy = np.meshgrid(self.x, self.y)

        self.frame = None
        self.moments = None

        self.SMALL_CHANGES = small_changes
        self.force_roundish = force_roundish

    @property
    def shape(self):
        return (self.leny, self.lenx, 3)

    @shape.setter
    def shape(self, yx):
        assert isinstance(yx, tuple), 'must be tuple'
        self.leny, self.lenx = yx
        self.x = np.linspace(0, self.lenx - 1, self.lenx)
        self.y = np.linspace(0, self.leny - 1, self.leny)
        self.xx, self.yy = np.meshgrid(self.x, self.y)

    def read(self):
        if self.SMALL_CHANGES:
            img, self.moments = misc.simulate_peaks(moments=self.moments)
        if self.force_roundish:
            img, self.moments = misc.simulate_peaks(moments=self.moments, )
        else:
            img, self.moments = misc.simulate_peaks()
        return True, img

    def reset_moments(self):
        self.moments = None

    def get(self, prop):
        if prop.upper() in 'CV_CAP_PROP_FRAME_WIDTH':
            return self.lenx
        elif prop.upper() in 'CV_CAP_PROP_FRAME_HEIGHT':
            return self.leny
        else:
            pass

    def set(self, prop, val):
        if prop.upper() in 'CV_CAP_PROP_FRAME_WIDTH':
            self._reshape(self, self.lenx, val)
        elif prop.upper() in 'CV_CAP_PROP_FRAME_HEIGHT':
            self._reshape(self, val, self.leny)
        else:
            pass

    def release(self):
        print('correctly terminated simulated cam')


class Camera(object):

    def __init__(self, address=None, revert_colors=True):
        self.address = address
        if self.address is None:
            self.cam = SimCam()
        else:
            self.cam = cv2.VideoCapture(self.address)
        self.frames = []
        self.revert_colors = revert_colors

    def read_multiple(self, n, timeout=10):
        assert isinstance(n, int), 'number of frames must be integer'
        frames = []
        i = 0
        while len(frames) < n:
            r_, frame = self.read()
            if r_:
                frames.append(frame)
            else:

                i += 1
                time.sleep(.1)
            if i > timeout:
                break
        avgframe = np.zeros_like(frame)
        for frame in frames:
            avgframe += frame
        return avgframe

    def read(self):
        r_, frame = self.cam.read()
        if r_ and self.revert_colors and len(frame.shape) == 3:
            frame = frame[..., ::-1]
        return r_, frame

    def grab(self):
        return self.cam.grab()

    def isOpened(self):
        return self.cam.isOpened()

    def release(self):
        return self.cam.release()

    def retrieve(self):
        return self.cam.retrieve()

    def set(self, prop, val):
        if type(prop) == str:
            prop = prop_id(prop)
        return (self.cam.set(prop, val))

    def get(self, prop):
        if type(prop) == str:
            prop = prop_id(prop)
        return (self.cam.get(prop))

    def __del__(self):
        self.cam.release()

    def snapshot(self):
        r_, frame = self.read()
        if r_:
            plt.figure('snapshot')
            plt.imshow(frame)
            plt.show()

    def maximise_resolution(self):
        self.set('width', 1920)
        self.set('height', 1080)

    def get_resolution(self):
        x = self.get(3)
        y = self.get(4)
        return (x, y)


def main():
    pass


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    cam = Camera()
    r_, img = cam.read()
    plt.imshow(img)
    plt.show()
