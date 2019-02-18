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
import sys
import numpy as np
from PyQt5 import QtWidgets, uic

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt



def raise_Qerror(doingWhat, errorHandle, type='Warning', popup=True):
    """ opens a dialog window showing the error"""
    errorMessage = 'Thread Error while {0}:\n{1}'.format(doingWhat, errorHandle)
    print(errorMessage)
    if popup:
        errorDialog = QtWidgets.QMessageBox()
        errorDialog.setText(errorMessage)
        if type == 'Warning':
            errorDialog.setIcon(QtWidgets.QMessageBox.Warning)
        elif type == 'Critical':
            errorDialog.setIcon(QtWidgets.QMessageBox.Critical)
        errorDialog.setStandardButtons(QtWidgets.QMessageBox.Ok)
        errorDialog.exec_()

def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)

def recompile(folder):
    print('recompiling')
    uic.compileUiDir(folder, execute=True)
    print('done')


class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=6, height=6, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.draw_figure()

    def draw_figure(self):
        plt.style.use('default')
        plt.style.use('seaborn-paper')
        self.mainax = self.figure.add_axes([.05, .30, .65, .65], xticklabels=[], yticklabels=[])
        self.xax = self.figure.add_axes([.05, .05, .65, .20], yticklabels=[])
        self.yax = self.figure.add_axes([.75, .30, .20, .65], xticklabels=[])
        self.yax.yaxis.tick_right()
        for ax in [self.mainax, self.xax, self.yax]:
            ax.tick_params(axis="both", direction="in", bottom=True, top=True, left=True, right=True, which='both')
        self.xax.xaxis.set_ticks_position('both')
        self.xax.xaxis.set_label_position("bottom")
        self.yax.yaxis.set_ticks_position('both')
        self.yax.yaxis.set_label_position("right")


    def draw_fit_result(self,xx,yy,data,fit_data, n_levels, colors='w'):
        lenx, leny = xx.shape
        x = np.linspace(0,lenx-1,lenx)
        y = np.linspace(0,leny-1,leny)
        self.mainax.cla()
        self.xax.cla()
        self.yax.cla()
        self.mainax.imshow(data)
        self.mainax.contour(xx, yy, fit_data, n_levels, colors=colors)
        self.xax.plot(x, data.sum(axis=0))
        self.xax.plot(x, fit_data.sum(axis=0))
        self.yax.plot(-data.sum(axis=1),y)
        self.yax.plot(-fit_data.sum(axis=1),y)
        self.draw()



def main():
    pass


if __name__ == '__main__':
    main()
