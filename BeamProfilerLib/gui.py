# -*- coding: utf-8 -*-
"""
Created on Fri June  23 09:30:00 2017

@author: S.Y. Agustsson
"""

import sys
import numpy as np

import cv2
import pyqtgraph as pg
from PyQt5 import QtWidgets as qw, QtCore as qc, QtGui as qg

class CamView(qw.QWidget):
    """ main Widget showing simple video from camera."""

    # Parameters:

    CAMERA = 2
    AVERAGES = 10


    def __init__(self):
        super(CamView, self).__init__()

        layout = qw.QGridLayout()  # create a grid for subWidgets
        layout.setSpacing(10)
        self.setLayout(layout)

        self.camWindow = pg.ImageView()
        layout.addWidget(self.camWindow, 0,0,1,1)

        self.timer = qc.QTimer()
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.on_timer)
        self.timer.start()

        self.frames = []
        self.frame = np.array([])
        self.frame_number = 0
        self.fig = np.array([])

        self.cam = cv2.VideoCapture(self.CAMERA)

        self.show()

    # def on_timer(self):  # todo: implement averages, this doesnt work
    #     ret, self.frame = self.cam.read()
    #     if self.frame_number < self.AVERAGES:
    #         self.frame_number +=1
    #         self.frames.append(self.convert_frame(self.frame))
    #     else:
    #         self.frame_number = 0
    #         for i, j in range(len(self.frame[0])), range(len(self.frame[0][0])):
    #             r = 0
    #             g = 0
    #             b = 0
    #
    #             for n in range(self.AVERAGES):
    #                 r += self.frame[n][i][j][0]
    #                 g += self.frame[n][i][j][1]
    #                 b += self.frame[n][i][j][2]
    #             r /= self.AVERAGES
    #             b /= self.AVERAGES
    #             g /= self.AVERAGES
    #             self.fig[i][j] = np.array([r,g,b], dtype='unit8')
    #         self.camWindow.setImage(self.fig,
    #                                 axes={'x': 1, 'y': 0, 'c': 2})  # transpose the matrix to rotate correctly the image
    #         self.frames = []

    def on_timer(self):
        self.refresh_frame()
    def refresh_frame(self):
        average = False
        frames = []
        if average:
            avgs = 50
            fig= np.array([])
            for n in range(avgs):
                ret, frame = self.cam.read()
                frames.append(self.convert_frame(frame))
            for i, j in range(len(frame[0])), range(len(frame[0][0])):
                r = 0
                g = 0
                b = 0

                for n in range(avgs):
                    r += frame[n][i][j][0]
                    g += frame[n][i][j][1]
                    b += frame[n][i][j][2]
                r /= avgs
                b /= avgs
                g /= avgs
                fig[i][j] = np.array([r,g,b], dtype='unit8')
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
