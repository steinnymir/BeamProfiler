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

def main():
    # img = get_frame()
    # # y_len = len(img)
    # # x_len = len(img[0])
    #
    # # mono_img = np.ones([y_len,x_len])
    # mono_img = np.ones([480,640])
    # for i in range(480):
    #     for j in range(640):
    #         mono_img[i][j] = img.item(i,j,0)
    # ax = plt.subplot(111)
    #
    # ax.pcolorfast(mono_img, cmap='RdBu')
    # plt.show()
   show_webcam()


def show_webcam():
    cam = cv2.VideoCapture(1)
    while True:
        ret_val, img = cam.read()

        y_len = len(img)
        x_len = len(img[0])
        mono_img = np.ones([y_len,x_len])
        # for i in range(y_len):
        #     for j in range(x_len):
        #         mono_img[i][j] = img.item(i,j,1)
        mono_img = (img[:,:,0] + img[:,:,1] + img[:,:,2])
        cv2.imshow('logitech webcam', mono_img)
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

        self.gauss_img = misc.imread('c://py_code//BeamProfiler//test_data//gauss01.png')

        self.camWindow = pg.ImageView()
        layout.addWidget(self.camWindow, 0, 2, 3, 4)
        self.camWindow.setImage(self.gauss_img)
        colors = [(0, 0, 0),(255, 255, 255)]
        cmap = pg.ColorMap(pos=np.linspace(0.0, 1.0, 2), color=colors)
        self.camWindow.setColorMap(cmap)

        self.start_btn = qw.QPushButton('Start Video')
        layout.addWidget(self.start_btn, 0, 0)
        self.start_btn.setCheckable(True)
        self.start_btn.clicked.connect(self.start_acquisition)

        self.gauss_btn = qw.QPushButton('Show Gaussian')
        layout.addWidget(self.gauss_btn, 2, 0)
        # self.gauss_btn.setCheckable(True)
        self.gauss_btn.clicked.connect(self.show_gaussian)

        # self.avg_input = qw.QTextEdit()
        # layout.addWidget(self.avg_input, 1, 0,1,1)



        self.fps_display = qw.QLabel('0')
        layout.addWidget(self.fps_display, 1,1)



        self.fps = 0


        self.timer = qc.QTimer()
        self.timer.setInterval(1)
        self.timer.timeout.connect(self.on_timer)
        self.timer.start()


        self.cam = cv2.VideoCapture(self.CAMERA)

        self.show()

    def on_timer(self):
        if not self.start_btn.isChecked():
            # self.AVERAGES = self.avg_input.text()
            self.refresh_frame()
            self.fps_display.setText('      FPS: {0:3.1F}'.format(self.fps))

    def start_acquisition(self):
        if self.start_btn.isChecked():
            self.start_btn.setText('Stop Video')
        else:
            self.start_btn.setText('Start Video')

    def show_gaussian(self):
        try:
            self.camWindow.setImage(self.gauss_img)
        except FileNotFoundError:
            print('file not found')

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
            fig = self.monochromatize(frame, color=color)
            self.camWindow.setImage(fig, axes={'x':1, 'y':0})  # transpose the matrix to rotate correctly the image
        self.fps = (1 / (time.time() - t_0 ))

    @staticmethod
    def monochromatize(img, size=CAM_RESOLUTION, color='all'):
        """

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