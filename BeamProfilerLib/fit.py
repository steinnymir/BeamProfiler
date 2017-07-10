# -*- coding: utf-8 -*-
"""
Created on Fri June July 37 09:30:00 2017

@author: S.Y. Agustsson
"""

import numpy as np
import scipy
from scipy import misc
import scipy.optimize as opt
import matplotlib.pyplot as plt

def main():

    gaussFig = misc.imread('..//test_data//gauss01.png')
    print(gaussFig.shape)

    data = GaussFit.gaussian(5, 0, 0, 3, 2, 0)
    print(data)
    fit = GaussFit.fitgaussian(data)
    # print(fit)



class GaussFit(object):

    def __init__(self):
        asd = 0

    @staticmethod
    def gaussian(height, center_x, center_y, width_x, width_y, rotation):
        """Returns a gaussian function with the given parameters"""
        width_x = float(width_x)
        width_y = float(width_y)

        rotation = np.deg2rad(rotation)
        center_x = center_x * np.cos(rotation) - center_y * np.sin(rotation)
        center_y = center_x * np.sin(rotation) + center_y * np.cos(rotation)

        def rotgauss(x, y):
            xp = x * np.cos(rotation) - y * np.sin(rotation)
            yp = x * np.sin(rotation) + y * np.cos(rotation)
            g = height * np.exp(
                -(((center_x - xp) / width_x) ** 2 +
                  ((center_y - yp) / width_y) ** 2) / 2.)
            return g

        return rotgauss

    @staticmethod
    def moments(data):
        """Returns (height, x, y, width_x, width_y)
        the gaussian parameters of a 2D distribution by calculating its
        moments """
        total = data.sum()
        X, Y, z = np.indices(data.shape)
        x = (X * data).sum() / total
        y = (Y * data).sum() / total
        col = data[:, int(y)]
        width_x = np.sqrt(abs((np.arange(col.size) - y) ** 2 * col).sum() / col.sum())
        row = data[int(x), :]
        width_y = np.sqrt(abs((np.arange(row.size) - x) ** 2 * row).sum() / row.sum())
        height = data.max()
        return height, x, y, width_x, width_y, 0.0

    def fitgaussian(self, data):
        """Returns (height, x, y, width_x, width_y)
        the gaussian parameters of a 2D distribution found by a fit"""
        params = self.moments(data)
        errorfunction = lambda p: np.ravel(self.gaussian(*p)(*np.indices(data.shape)) - data)
        p, success = opt.leastsq(errorfunction, params)

        return p

################################################################################################
################################################################################################
################################################################################################

def twoD_Gaussian(x, y, amplitude, xo, yo, sigma_x, sigma_y, theta, offset):
    xo = float(xo)
    yo = float(yo)
    a = (np.cos(theta) ** 2) / (2 * sigma_x ** 2) + (np.sin(theta) ** 2) / (2 * sigma_y ** 2)
    b = -(np.sin(2 * theta)) / (4 * sigma_x ** 2) + (np.sin(2 * theta)) / (4 * sigma_y ** 2)
    c = (np.sin(theta) ** 2) / (2 * sigma_x ** 2) + (np.cos(theta) ** 2) / (2 * sigma_y ** 2)
    g = offset + amplitude * np.exp(- (a * ((x - xo) ** 2) + 2 * b * (x - xo) * (y - yo)
                                       + c * ((y - yo) ** 2)))
    return g.ravel()


def createData():
    x = np.linspace(0, 200, 201)
    y = np.linspace(0, 200, 201)
    x, y = np.meshgrid(x, y)

    # create data
    data = twoD_Gaussian(x, y, 3, 100, 100, 20, 40, 0, 10)

    # plot twoD_Gaussian data generated above
    plt.figure()
    plt.imshow(data.reshape(201, 201))
    plt.colorbar()

    initial_guess = (3, 100, 100, 20, 40, 0, 10)

    data_noisy = data + 0.2 * np.random.normal(size=data.shape)

    popt, pcov = opt.curve_fit(twoD_Gaussian, x, y, data_noisy, p0=initial_guess)
    data_fitted = twoD_Gaussian(x, y, *popt)

    fig, ax = plt.subplots(1, 1)
    ax.hold(True)
    ax.imshow(data_noisy.reshape(201, 201), cmap=plt.cm.jet, origin='bottom',
              extent=(x.min(), x.max(), y.min(), y.max()))
    ax.contour(x, y, data_fitted.reshape(201, 201), 8, colors='w')
    plt.show()

if __name__=="__main__":

    main()