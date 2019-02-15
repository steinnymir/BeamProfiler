# -*- coding: utf-8 -*-
"""

@author: Steinn Ymir Agustsson

    Copyright (C) 2019 Steinn Ymir Agustsson

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

from PyQt5.QtWidgets  import QMainWindow, QWidget, QGridLayout, QVBoxLayout,QPushButton,QRadioButton, QGroupBox, QLabel
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont
import cv2
import pyqtgraph as pg

import numpy as np
from pyqtgraph.widgets import MatplotlibWidget

from utilities import misc

class BeamProfilerMainApp(QMainWindow):
    _SIMULATE = True
    def __init__(self):
        super(BeamProfilerMainApp, self).__init__()
        self.setWindowTitle('Beam Profiler')
        self.setGeometry(100, 50, 1000, 600)

        self.status_bar = self.statusBar()
        self.status_bar.showMessage('ready')

        # set the cool dark theme and other plotting settings
        # self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        pg.setConfigOption('background', .99)
        pg.setConfigOption('foreground', .01)
        pg.setConfigOptions(antialias=True)

        self.initialize_camera(1)
        self.video_timer = QTimer()
        self.video_timer.setInterval(100)
        self.video_timer.timeout.connect(self.on_video_timer)
        self.video_timer_on = False
        # self.start_stop_video_timer()

        self.peak_moments = None
        self.sim_moments = None
        self.meshgrid = None
        self.data_fitted = None
        self.zoom_frame = None
        self.box_size = 1
        self.setupUi()

    def setupUi(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.main_layout = QGridLayout(self)
        self.central_widget.setLayout(self.main_layout)

        self.camera_widget = pg.ImageView(name='CameraFeed',view=pg.PlotItem())
        self.camera_widget.ui.histogram.hide()
        self.camera_widget.ui.roiBtn.hide()
        self.camera_widget.ui.menuBtn.hide()
        self.main_layout.addWidget(self.camera_widget, 0, 0, 4, 3)
        self.fit_img_widget = pg.ImageView(name='fitted data',view=pg.PlotItem())
        self.fit_img_widget.ui.histogram.hide()
        self.fit_img_widget.ui.roiBtn.hide()
        self.fit_img_widget.ui.menuBtn.hide()


        self.main_layout.addWidget(self.fit_img_widget, 2,3,2,2)

        self.controlbox = QGroupBox('controls')
        self.main_layout.addWidget(self.controlbox,0,3,1,2)
        self.controlbox_layout = QGridLayout()
        self.controlbox.setLayout(self.controlbox_layout)

        self.start_stop_button = QPushButton('start/stop')
        self.controlbox_layout.addWidget(self.start_stop_button,0,0,1,1)
        self.start_stop_button.clicked.connect(self.start_stop_video_timer)

        self.plt_print_button = QPushButton('matplotlib')
        self.controlbox_layout.addWidget(self.plt_print_button,2,0,1,1)
        self.plt_print_button.clicked.connect(self.plot_matplotlib)

        self.fit_checkbox = QRadioButton('fit')
        self.controlbox_layout.addWidget(self.fit_checkbox,1,0,1,1)

        self.resultsbox = QGroupBox('Fit Results')
        self.main_layout.addWidget(self.resultsbox,1,3,1,2)
        self.resultsbox_layout = QGridLayout()
        self.resultsbox.setLayout(self.resultsbox_layout)



        self.fit_results_text = QLabel('Start fitting to show results')
        self.fit_results_text.setFont(QFont("Times", 8, QFont.Bold))
        self.resultsbox_layout.addWidget(self.fit_results_text,0,0)
        self.fit_mainresults_text = QLabel('')
        self.fit_mainresults_text.setFont(QFont("Times", 12, QFont.Bold))
        self.resultsbox_layout.addWidget(self.fit_mainresults_text,0,1)

        # self.plt_widget = MatplotlibWidget.MatplotlibWidget()
        # self.main_layout.addWidget(self.plt_widget,0,0,5,5)
        # self.subplot = self.plt_widget.getFigure().add_subplot(111)

    def start_stop_video_timer(self):
        if self.video_timer_on:
            self.video_timer.stop()
            self.video_timer_on = False
        else:
            self.video_timer.start()
            self.video_timer_on = True

    def plot_matplotlib(self):
        import matplotlib.pyplot as plt
        f = plt.figure()
        ax = f.add_subplot(111)

        x = np.linspace(0, self.box_size - 1, self.box_size)
        x, y = np.meshgrid(x, x)
        ax.imshow(self.zoom_frame)
        plt.contour(x, y, self.data_fitted.reshape(self.box_size,self.box_size), 3, colors='w')
        plt.show()
        # x = np.linspace(0,)
        # ax.contour(x, y, fit, 3, colors='w')


    def on_video_timer(self):
        if self._SIMULATE:
            self.frame, self.sim_moments = misc.simulate_peaks(moments=self.sim_moments)
        else:
            self.frame = self.get_frame()

        if self.frame is not None:
            self.draw_frame(self.frame)
            if self.fit_checkbox.isChecked():
                self.fit_peaks(self.frame)

    def fit_peaks(self,frame):
        try:
            self.peak_moments, perr = misc.fit_2d_gaussian(frame)
            l = []
            for a in zip(['Amplitude', 'X center', 'Y Center', 'sigma X', 'sigma Y', 'Theta', 'Offset'], self.peak_moments):
                l.append(a[0])
                l.append(a[1])
            text = '{:15}:{:5.3f}\n{:15}:{:5.3f}\n{:15}:{:5.3f}\n{:15}:{:5.3f}\n{:15}:{:5.3f}\n{:15}:{:5.3f}\n{:15}:{:5.3f}\n'.format(*l)
            self.fit_results_text.setText(text)
            A = self.peak_moments[3]*self.peak_moments[3]*np.pi /4
            r = np.sqrt(A/np.pi)
            maintext = '{:15}:{:5.3f}\n{:15}:{:5.3f}'.format('Area',A,'~Radius',r)
            self.fit_mainresults_text.setText(maintext)

        except:
            pass

    def draw_frame(self,frame):
        if self._SIMULATE:
            self.camera_widget.setImage(frame, axes={'x': 1, 'y': 0})

            if self.peak_moments is not None:
                # if self.meshgrid is None:
                self.box_size = int(max(self.peak_moments[3]*5,self.peak_moments[4]*5,self.box_size))
                meshgrid = misc.make_meshgrid(self.box_size,self.box_size)
                zoom_moments = []
                for i, moment in enumerate(self.peak_moments):
                    if i in [1,2]:
                        zoom_moments.append(self.box_size/2)
                    else:
                        zoom_moments.append(moment)

                self.data_fitted = misc.gauss_2d(meshgrid, *zoom_moments).reshape(self.box_size,self.box_size)
                yo,xo = misc.find_maxima(frame)
                self.zoom_frame = frame[int(yo-self.box_size/2):int(yo+self.box_size/2),
                             int(xo-self.box_size/2):int(xo+self.box_size/2)]
                # self.fit_img_widget.setImage(data_fitted.reshape(self.box_size,self.box_size), axes={'x': 1, 'y': 0})
                img = self.fit_img_widget.setImage(self.zoom_frame, axes={'x': 1, 'y': 0})
                # iso = pg.IsocurveItem(data_fitted,level=2,pen='g')
                # iso.setParentItem(img)
                # self.fit_img_widget.addItem(iso)


        else:
            if len(frame[0][0]) == 3:
                self.camera_widget.setImage(frame, axes={'x': 1, 'y': 0, 'c': 2})
            else:
                print(len(frame[0][0]))
                self.camera_widget.setImage(frame, axes={'x': 1, 'y': 0})

    def initialize_camera(self,address):
        self.camera = cv2.VideoCapture(address)

    def get_frame(self):
        ret_val, img = self.camera.read()
        if ret_val:
            return img

    def closeEvent(self, event):
        # geometry = self.saveGeometry()
        # self.qsettings.setValue('geometry', geometry)
        print('quitted properly')
        super(BeamProfilerMainApp, self).closeEvent(event)


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('Step StepScan Meter')
        self.setGeometry(100, 50, 800, 900)

        self.status_bar = self.statusBar()
        self.status_bar.showMessage('ready')
        self.makeMenuBar()

        # set the cool dark theme and other plotting settings
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        pg.setConfigOption('background', 0.1)
        pg.setConfigOption('foreground', 0.7)
        pg.setConfigOptions(antialias=True)

        self.makeLayout()

    def makeLayout(self):
        self.dock_area = DockArea()
        self.setCentralWidget(self.dock_area)

        # self.setupUi(self)
        # self.qsettings = QtCore.QSettings('DemsarLabs','StepScanMeter')
        # geometry = self.qsettings.value('geometry', '')

        self.scan_area = ScanAreaWidget()
        self.scan_area_docker = QtWidgets.QDockWidget()
        self.scan_area_docker.setObjectName("docker")
        # self.plot_area_docker.setAllowedAreas(QtCore.Qt.TopDockWidgetArea)
        self.scan_area_docker.setWidget(self.scan_area)

        self.scan_setup_area = ScanSetupWidget()
        self.scan_setup_area_docker = QtWidgets.QDockWidget()
        self.scan_setup_area_docker.setObjectName('Scan Setup Area')
        # self.scan_setup_area_docker.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea)
        self.scan_setup_area_docker.setWidget(self.scan_setup_area)

        self.scan_setup_area.set_scan_settings.connect(self.scan_area.acceptScanSettings)
        self.instrument_monitor = DockInstrumentMonitor()

        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.scan_setup_area_docker)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.scan_area_docker)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.instrument_monitor)
        # self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.scan_monitor)
        # self.restoreGeometry(geometry)


def main():
    pass


if __name__ == '__main__':
    main()