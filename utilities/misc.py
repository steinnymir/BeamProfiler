# -*- coding: utf-8 -*-
"""

@author: Steinn Ymir Agustsson

    Copyright (C) 2018 Steinn Ymir Agustsson

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
import numpy as np
import scipy.optimize as opt
import cv2

def make_2d_gaussian_img(size=(600, 800), seed=None, noise=1,
                         amplitude=None, xo=None, yo=None, sigma_x=None, sigma_y=None, theta=None, offset=None,
                         return_moments=False, moments=None,force_roundish=False):
    lenx = size[1]
    leny = size[0]
    x = np.linspace(0, lenx - 1, lenx)
    y = np.linspace(0, leny - 1, leny)
    x, y = np.meshgrid(x, y)

    if seed is not None:
        np.random.seed(seed)

    noise = np.random.rand(lenx * leny) * noise
    if moments is not None:
        amplitude, xo, yo, sigma_x, sigma_y, theta, offset = moments
    if amplitude is None:
        amplitude = float(np.random.rand(1)) * 10
    if xo is None:
        xo = size[1] / 10 + float(np.random.rand(1)) * size[1] * .8
    if yo is None:
        yo = size[1] / 10 + float(np.random.rand(1)) * size[0] * .8
    if sigma_x is None:
        sigma_x = 5 + float(np.random.rand(1)) * 10
    if sigma_y is None:
        sigma_y = 5 + float(np.random.rand(1)) * 10
    if theta is None:
        theta = float(np.random.rand(1)) * np.pi
    if offset is None:
        offset = float(np.random.rand(1))

    if force_roundish:
        sigma_x = sigma_y = (sigma_x+sigma_y)/2
        sigma_x += float(np.random.rand(1)-.5)/(10*sigma_x)
        sigma_y += float(np.random.rand(1)-.5)/(10*sigma_y)

    g = gauss_2d((x, y), amplitude, xo, yo, sigma_x, sigma_y, theta, offset)
    g += noise
    if return_moments:
        return g.reshape(*size), (amplitude, xo, yo, sigma_x, sigma_y, theta, offset)
    else:
        return g.reshape(*size)


def gauss_2d(img, amplitude, xo, yo, sigma_x, sigma_y, theta, offset):
    (x, y) = img
    xo = float(xo)
    yo = float(yo)
    a = (np.cos(theta) ** 2) / (2 * sigma_x ** 2) + (np.sin(theta) ** 2) / (2 * sigma_y ** 2)
    b = -(np.sin(2 * theta)) / (4 * sigma_x ** 2) + (np.sin(2 * theta)) / (4 * sigma_y ** 2)
    c = (np.sin(theta) ** 2) / (2 * sigma_x ** 2) + (np.cos(theta) ** 2) / (2 * sigma_y ** 2)
    g = offset + amplitude * np.exp(- (a * ((x - xo) ** 2) + 2 * b * (x - xo) * (y - yo)
                                       + c * ((y - yo) ** 2)))
    return g.ravel()


def find_maxima(array):
    return np.unravel_index(array.argmax(), array.shape)


def fit_2d_gaussian(img, guess=None, bounds=None):
    """ attempt to fit a 2d gaussian to the given image

    :param img:
    :return:
    """

    if guess is None:
        yo, xo = find_maxima(img)
        amplitude = img[yo, xo]
        g = [amplitude, xo, yo, 15, 15, np.pi, 1]
    else:
        g = guess
    xo, yo = g[1], g[2]
    sx, sy = 2*g[3], 2*g[4]


    #     zoom_img = img[g[2]-g[4]:g[2]+g[4],g[1]-g[3]:g[1]+g[3]]
    zoom_img = img[yo - sy:yo + sy, xo - sx:xo + sx]
    g[1], g[2] = sx, sy

    if bounds is None:
        bounds = ((0, 0, 0, 0.1, 0.1, 0, -10), (np.inf, 2 * g[3], 2 * g[4], 20, 20, np.pi, np.inf))

    leny, lenx = zoom_img.shape
    x = np.linspace(0, lenx - 1, lenx)
    y = np.linspace(0, leny - 1, leny)
    x, y = np.meshgrid(x, y)

    popt, pcov = opt.curve_fit(gauss_2d, (x, y), zoom_img.ravel(), p0=g, bounds=bounds)
    perr = np.sqrt(np.diag(pcov))
    popt[1] += xo - sx
    popt[2] += yo - sy
    return popt, perr


def simulate_peaks(moments=None, pos_change=20, moment_change=50, force_roundish=True):
    if moments is None:
        frame, moments = make_2d_gaussian_img(return_moments=True,force_roundish=force_roundish)
        return frame, moments
    else:
        new_moments = []
        for i, par in enumerate(moments):
            if i in [1,2]:
                new_moments.append(par + np.random.randn()*par/moment_change)
            else:
                new_moments.append(par + np.random.randn()*par/pos_change)

        frame = make_2d_gaussian_img(moments=new_moments,force_roundish=force_roundish)
    return frame, new_moments


def make_meshgrid(lenx,leny):
    x = np.linspace(0, lenx - 1, lenx)
    y = np.linspace(0, leny - 1, leny)
    x, y = np.meshgrid(x, y)
    return x,y


def _timing_test():
    import time
    size=(480,640)
    tests = 100

    times = []
    for i in range(tests):
        img, moments = make_2d_gaussian_img(size=size, noise=2, return_moments=True)
        t0 = time.time()
        popt, perr = fit_2d_gaussian(img, guess=None, bounds=None)
        print('-------------\nattempt{}\n--------------'.format(i + 1))
        print('{:6.3f}|{:5.0f}|{:5.0f}|{:5.2f}|{:5.2f}|{:5.2f}|{:5.2f}|'.format(*moments))
        print('{:6.3f}|{:5.0f}|{:5.0f}|{:5.2f}|{:5.2f}|{:5.2f}|{:5.2f}|'.format(*popt))
        print('{:6.3f}|{:5.0f}|{:5.0f}|{:5.2f}|{:5.2f}|{:5.2f}|{:5.2f}|'.format(
            *[100 * (x - y) / x for x, y in zip(moments, popt)]))
        times.append(time.time() - t0)
        print('it took: {}'.format(times[-1]))
    times = np.array(times)
    print('--------------\nmean: {}\nmin: {}\nmax: {}'.format(times.mean(), times.min(), times.max()))




if __name__ == '__main__':
    _timing_test()
