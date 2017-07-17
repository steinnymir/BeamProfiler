# -*- coding: utf-8 -*-
"""
Created on Fri June  23 09:28:43 2017

@author: S.Y. Agustsson
"""

import sys

import cv2
import pyqtgraph as pg
from PyQt5 import QtWidgets as qw, uic

from scipy import misc
import scipy.optimize as opt
import numpy as np
import matplotlib.pyplot as plt

from BeamProfilerLib.gui import CamView

Ui_MainWindow, QtBaseClass = uic.loadUiType('BeamProfilerUI.ui')


def main():

    app = qw.QApplication(sys.argv)
    w = MainApp()
    # w.setGeometry(300, 100, 640, 480)
    w.show()
    app.exec_()


class MainApp(qw.QMainWindow, ):

    def __init__(self):
        super(MainApp,self).__init__()
        self.ui = Ui_MainWindow()

        self.ui.setupUI(self)
        self.show()
        #
        #
        # self.layout = qw.QGridLayout()  # create a grid for subWidgets
        # self.layout.setSpacing(10)
        # self.setLayout(self.layout)
        #
        # self.centralWidget = CamView()
        # self.layout.addWidget(self.centralWidget, 0, 0)
        # self.setCentralWidget(self.centralWidget)
        #
        # self.statusBar = qw.QStatusBar()
        # self.setStatusBar(self.statusBar)
        # self.statusBar.addWidget(qw.QLabel("message left 1"))


        self.show()



if __name__== "__main__":

    # main()
    ui_file = 'C:\py_code\BeamProfiler\BeamProfilerLib\BeamProfilerUI.ui'
    py_file = open('C:\py_code\BeamProfiler\BeamProfilerLib\BeamProfilerUI.py', 'w')
    uic.compileUi(ui_file, py_file, execute=True)