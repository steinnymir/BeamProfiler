# -*- coding: utf-8 -*-
"""
Created on Fri June  23 09:28:43 2017

@author: S.Y. Agustsson
"""

import sys
from PyQt5 import QtWidgets as qw, QtCore as qc, uic
import cv2
from BeamProfilerLib.BeamProfilerUI import Ui_MainWindow
from BeamProfilerLib.gui import get_frame, get_devicelist, get_weighted_frame

def main():

    app = qw.QApplication(sys.argv)
    w = BeamProfilerMainApp()
    # w.setGeometry(300, 100, 640, 480)
    w.show()
    app.exec_()


class BeamProfilerMainApp(qw.QMainWindow, Ui_MainWindow):

    CAMERA = 1

    def __init__(self):
        super(BeamProfilerMainApp,self).__init__()

        self.setupUi(self)

        self.timer = qc.QTimer()
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.on_timer)

        self.camera = cv2.VideoCapture(self.CAMERA)

        self.show()



    def init_camera(self):
        if isinstance(self.camera, cv2.VideoCapture()):
            del self.camera
        self.camera = cv2.VideoCapture(self.CAMERA)


    @qc.pyqtSlot()
    def on_timer(self): # todo: wokrk on this
        frame = get_frame(self.camera, color='RGB')

        if len(frame[0][0]) == 3:
            self.cam_window.setImage(frame, axes={'x': 1, 'y': 0, 'c':2})
        else:
            print(len(frame[0][0]))
            self.cam_window.setImage(frame, axes={'x': 1, 'y': 0})

    @qc.pyqtSlot()
    def save_screenshot(self):
        print('it works: save screenshot')

    @qc.pyqtSlot()
    def start_recording(self):
        print('it works: start recording')
        self.timer.start()
        print('Timer Started')

    @qc.pyqtSlot()
    def start_aquisition(self):
        print('it works: start aquisition')


if __name__== "__main__":

    recompile = True
    if recompile:
        print('recompiling')
        ui_file = 'C:\py_code\BeamProfiler\BeamProfilerLib\BeamProfilerUI.ui'
        ui_dir = 'C:\py_code\BeamProfiler\BeamProfilerLib'
        # py_file = open('C:\py_code\BeamProfiler\BeamProfilerLib\BeamProfilerUI.py', 'w')
        uic.compileUiDir(ui_dir, execute=True)
        print('done')

    main()