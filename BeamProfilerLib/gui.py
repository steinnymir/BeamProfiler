# -*- coding: utf-8 -*-
"""
Created on Fri June  23 09:30:00 2017

@author: S.Y. Agustsson
"""

import sys
import numpy as np
from scipy import misc
import matplotlib.pyplot as plt
from matplotlib import cm
import cv2
import pyqtgraph as pg
from PyQt5 import QtWidgets as qw, QtCore as qc, QtGui as qg
import time
import VideoCapture
import pickle

def main():

    print(get_devicelist())
    show_webcam(0)


def get_devicelist():
    """ Returns a dictionary of device names with corresponding port value and max resolution"""
    try:
        from VideoCapture import Device
        useVC = True
    except ImportError:
        useVC = False
        print('VideoCapture is not correctly installed. No device name can be obtained')
    devices = {}
    for i in range(10):
        try:
            import vidcap
            if useVC:
                dev = Device(i)
                dev_name = dev.getDisplayName()
                devices[dev_name] = {'port': i}
                del dev
            else:
                dev_name = 'camera{}'.format(i)

            devices[dev_name] = {}
            cam = cv2.VideoCapture(i)
            # cam.set(cv2.CAP_PROP_FRAME_WIDTH, 5000)  # force maximum resolution by overshooting
            # cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 5000)  # force maximum resolution by overshooting
            w = cam.get(cv2.CAP_PROP_FRAME_WIDTH)
            h = cam.get(cv2.CAP_PROP_FRAME_HEIGHT)
            devices[dev_name]['resolution'] = [w, h]
            devices[dev_name]['port'] = i
            del cam
        except vidcap.error:
            break
    return devices

def show_webcam(camnum):
    # temp_name = VideoCapture.Device(1).getDisplayName()
    # name = temp_name
    # del temp_name
    cam = cv2.VideoCapture(camnum)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 5000)  # force maximum resolution by overshooting
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 5000)  # force maximum resolution by overshooting
    # cam = VideoCapture.Device(1)

    while True:
        ret_val, img = cam.read()
        cv2.imshow('logitech webcam', img)
        if cv2.waitKey(1) == 27:
            break


def get_frame():
    cam = cv2.VideoCapture(1)
    ret_val, img = cam.read()
    return img


class CamView(qw.QWidget):
    """ main Widget showing simple video from camera."""

    # Parameters:

    CAMERA = 1
    CAM_RESOLUTION = [480,640]  # as [y,x]
    AVERAGES = 4


    def __init__(self):
        super(CamView, self).__init__()

        layout = qw.QGridLayout()  # create a grid for subWidgets
        layout.setSpacing(10)
        self.setLayout(layout)

        self.camWindow = pg.GraphicsView()
        layout.addWidget(self.camWindow, 0, 2, 10, 10)
        # self.camWindow.setImage(self.gauss_img)
        # colors = [(0, 0, 0),(255, 255, 255)]
        # cmap = pg.ColorMap(pos=np.linspace(0.0, 1.0, 2), color=colors)
        # self.camWindow.setColorMap(cmap)

        self.start_btn = qw.QPushButton('Start Video')
        layout.addWidget(self.start_btn, 0, 0)
        self.start_btn.setCheckable(True)
        self.start_btn.clicked.connect(self.start_acquisition)

        self.gauss_btn = qw.QPushButton('Show Gaussian')
        layout.addWidget(self.gauss_btn, 2, 0)
        # self.gauss_btn.setCheckable(True)
        # self.gauss_btn.clicked.connect(self.save_picture)

        self.save_name = qw.QTextEdit()
        layout.addWidget(self.save_name, 1, 0)
        self.devices = {}
        self.get_devicelist()


        self.fps_display = qw.QLabel('0')
        layout.addWidget(self.fps_display, 1,1)



        self.fps = 0


        self.timer = qc.QTimer()
        self.timer.setInterval(1)
        self.timer.timeout.connect(self.on_timer)
        self.timer.start()


        self.cam = cv2.VideoCapture(self.CAMERA)

        self.show()

    @qc.pyqtSlot()
    def on_timer(self):
        if not self.start_btn.isChecked():
            # self.AVERAGES = self.avg_input.text()
            self.refresh_frame()
            self.fps_display.setText('      FPS: {0:3.1F}'.format(self.fps))

    @qc.pyqtSlot()
    def start_acquisition(self):
        if self.start_btn.isChecked():
            self.start_btn.setText('Stop Video')
        else:
            self.start_btn.setText('Start Video')

    @qc.pyqtSlot()
    def show_gaussian(self):
        self.gauss_img = misc.imread('c://py_code//BeamProfiler//test_data//gauss01.png')
        try:
            self.camWindow.setImage(self.gauss_img)
        except FileNotFoundError:
            print('file not found')

    # @qc.pyqtSlot()
    # def save_picture(self):
    #     img = self.get_frame_average(10)
    #     savename = self.save_name.text()
    #
    #     file = open('e:/' + savename + '.obj', 'wb')
    #     pickle.dump(img,file)

    def get_frame_average(self, avg_n):
        _, f = self.cam.read()
        avg_img = np.float32(f)
        n = 0
        while n in range(avg_n):
            n += 1
            _, f = self.cam.read()
            cv2.accumulateWeighted(f, avg_img, 0.1)

        return avg_img

    def refresh_frame(self, color='all'):
        t_0 = time.time()
        average = True
        frames = []
        if average:
            frame = self.get_frame_average(self.AVERAGES)
        else:
            ret, frame = self.cam.read()

        if color == 'all':
            frame = self.bgr2rgb(frame)
            self.camWindow.setImage(frame, axes={'x': 1, 'y': 0, 'c':2})  # transpose the matrix to rotate correctly the image
        else:
            fig = self.get_intensity_array(frame, color=color)
            self.camWindow.setImage(fig, axes={'x':1, 'y':0})  # transpose the matrix to rotate correctly the image

        self.fps = (1 / (time.time() - t_0 ))



    @staticmethod
    def get_devicelist():
        """ Returns a dictionary of device names with corresponding port value and max resolution"""
        try:
            from VideoCapture import Device
            useVC = True
        except ImportError:
            useVC = False
            print('VideoCapture is not correctly installed. No device name can be obtained')
        devices = {}
        for i in range(10):
            try:
                import vidcap
                if useVC:
                    dev = Device(i)
                    dev_name = dev.getDisplayName()
                    devices[dev_name] = {'port': i}
                    del dev
                else:
                    dev_name = 'camera{}'.format(i)

                devices[dev_name] = {}
                cam = cv2.VideoCapture(i)
                cam.set(cv2.CAP_PROP_FRAME_WIDTH, 5000)  # force maximum resolution by overshooting
                cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 5000)  # force maximum resolution by overshooting
                w = cam.get(cv2.CAP_PROP_FRAME_WIDTH)
                h = cam.get(cv2.CAP_PROP_FRAME_HEIGHT)
                devices[dev_name]['resolution'] = [w, h]
                devices[dev_name]['port'] = i
                del cam
            except vidcap.error:
                break
        return devices



    @staticmethod
    def get_intensity_array(img, size=CAM_RESOLUTION, color='all'):
        """
            Reshape input image from RGB to single value per pixel.
        :param img: np.array
            np array from camera, as x, y, z, with z a tuple of 3 representing rgb color
        :param color: str
            determine which color to isolate:
            r, g, b, isolate red, green or blue, all gives sum of all
        :return: np.array
            2D array of pixels
        """
        mono_img = np.ones(size)

        if color == 'avg':
            mono_img = (img[:, :, 0] + img[:, :, 1] + img[:, :, 2])
        elif color == 'all':
            return img
        elif color == 'r':
            mono_img = img[:, :, 0]
        elif color == 'g':
            mono_img = img[:, :, 1]
        elif color == 'b':
            mono_img = img[:, :, 2]
        return mono_img

    @staticmethod
    def bgr2rgb(img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        return img

    def keyPressEvent(self, event):
        """Close application from escape key.

        results in QMessageBox dialog from closeEvent, good but how/why?
        """
        if event.key() == qc.Qt.Key_Escape:
            cv2.destroyAllWindows()
            self.cam.release()
            self.close()

    def run_video(self):

        vid = cv2.VideoCapture(self.CAMERA)
        ret, frame = vid.read()
        while ret:
            Qimg = self.bgr2rgb(frame)
            self.camWindow.setImage(Qimg)
            ret, frame = vid.read()
            qw.QApplication.processEvents()
            if cv2.waitKey(1) == 27:
                break


if __name__ == '__main__':
    main()