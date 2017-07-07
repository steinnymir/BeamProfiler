# -*- coding: utf-8 -*-
"""
Created on Fri June  23 09:30:00 2017

@author: S.Y. Agustsson
"""

import sys
import numpy as np
from scipy import misc

import cv2
import pyqtgraph as pg
from PyQt5 import QtWidgets as qw, QtCore as qc, QtGui as qg

class CamView(qw.QWidget):
    """ main Widget showing simple video from camera."""

    # Parameters:

    CAMERA = 0

    AVERAGES = 1


    def __init__(self):
        super(CamView, self).__init__()

        layout = qw.QGridLayout()  # create a grid for subWidgets
        layout.setSpacing(10)
        self.setLayout(layout)

        self.gauss_img = misc.imread('test_data//gauss01.png')

        self.camWindow = pg.ImageView()
        layout.addWidget(self.camWindow, 0, 0, 2, 3)
        self.camWindow.setImage(self.gauss_img)

        self.start_btn = qw.QPushButton('Start Video')
        layout.addWidget(self.start_btn, 1, 0, 1, 1)
        self.start_btn.setCheckable(True)
        self.start_btn.clicked.connect(self.start_acquisition)

        self.gauss_btn = qw.QPushButton('Show Gaussian')
        layout.addWidget(self.gauss_btn, 1, 1, 1, 1)
        # self.gauss_btn.setCheckable(True)
        self.gauss_btn.clicked.connect(self.show_gaussian)

        self.timer = qc.QTimer()
        self.timer.setInterval(1)
        self.timer.timeout.connect(self.on_timer)
        self.timer.start()

        self.cam = cv2.VideoCapture(self.CAMERA)

        self.show()

    def on_timer(self):
        if self.start_btn.isChecked():
            self.refresh_frame()

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


    def refresh_frame(self):
        average = True
        frames = []
        if average:
            frame = self.get_frame_average(self.AVERAGES)
        else:
            ret, frame = self.cam.read()
        frame = self.convert_frame(frame)
        fig = frame
        self.camWindow.setImage(fig, axes={'x':1, 'y':0, 'c':2})  # transpose the matrix to rotate correctly the image
        # self.camWindow.setPredefinedGradient('thermal')


    @staticmethod
    def convert_frame(img):
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
            Qimg = self.convert_frame(frame)
            self.camWindow.setImage(Qimg)
            ret, frame = vid.read()
            qw.QApplication.processEvents()
            if cv2.waitKey(1) == 27:
                break



        # vb = pg.ViewBox()
        # self.graphicsView.setCentralItem(vb)
        # vb.setAspectLocked()
        # img = pg.ImageItem()
        # vb.addItem(img)
        # vb.setRange(qc.QRectF(0, 0, 512, 512))


def show_webcam():
    cam = cv2.VideoCapture(1)
    while True:
        ret_val, img = cam.read()

        print(ret_val)
        cv2.imshow('logitech webcam', img)
        if cv2.waitKey(1) == 27:
            break
