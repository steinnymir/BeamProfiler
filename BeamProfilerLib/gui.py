# -*- coding: utf-8 -*-
"""
Created on Fri June  23 09:30:00 2017

@author: S.Y. Agustsson
"""

import sys

import cv2
import pyqtgraph as pg
from PyQt5 import QtWidgets as qw, QtCore as qc, QtGui as qg

class CamView(qw.QWidget):
    """ main Widget showing simple video from camera."""

    # Parameters:

    CAMERA = 1

    def __init__(self):
        super(CamView, self).__init__()

        layout = qw.QGridLayout()  # create a grid for subWidgets
        layout.setSpacing(10)
        self.setLayout(layout)

        self.camWindow = pg.ImageView()
        layout.addWidget(self.camWindow, 0,0,1,1)

        self.timer = qc.QTimer()
        self.timer.setInterval(20)
        self.timer.timeout.connect(self.on_timer)
        self.timer.start()

        self.cam = cv2.VideoCapture(self.CAMERA)

        self.show()

    def on_timer(self):
        self.refresh_frame()

    def refresh_frame(self):
        ret, frame = self.cam.read()
        frame = self.convert_frame(frame)
        self.camWindow.setImage(frame, axes={'x':1, 'y':0, 'c':2})  # transpose the matrix to rotate correctly the image
        # self.camWindow.setPredefinedGradient('thermal')


    @staticmethod
    def convert_frame(img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        return img



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

def plot_image():
    cam = cv2.VideoCapture(0)
    # print(type(cam.read()))
    ret_val, img = cam.read()

def show_webcam():
    cam = cv2.VideoCapture(1)
    while True:
        ret_val, img = cam.read()

        print(ret_val)
        cv2.imshow('logitech webcam', img)
        if cv2.waitKey(1) == 27:
            break
