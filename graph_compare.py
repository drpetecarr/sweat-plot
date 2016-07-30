import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from math import factorial


def savitzky_golay(y, window_size, order, deriv=1, rate=1):
    """
    Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
    The Savitzky-Golay filter removes high frequency noise from data.
    It has the advantage of preserving the original shape and
    features of the signal better than other types of filtering
    approaches, such as moving averages techniques.

    Parameters
    ----------
    y : array_like, shape (N,)
        the values of the time history of the signal.

    window_size : int
        the length of the window. Must be an odd integer number.

    order : int
        the order of the polynomial used in the filtering.
        Must be less then `window_size` - 1.

    deriv: int
        the order of the derivative to compute (default = 0 means only smoothing)

    Returns
    -------
    ys : ndarray, shape (N)
        the smoothed signal (or it's n-th derivative).

    Notes
    -----
    The Savitzky-Golay is a type of low-pass filter, particularly
    suited for smoothing noisy data. The main idea behind this
    approach is to make for each point a least-square fit with a
    polynomial of high order over a odd-sized window centered at
    the point.
    """

    try:
        window_size = np.abs(np.int(window_size))
        order = np.abs(np.int(order))
    except ValueError:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order + 1)
    half_window = (window_size - 1) // 2

    # pre-compute coefficients
    b = np.mat([[k ** i for i in order_range] for k in range(-half_window, half_window + 1)])
    x = np.linalg.pinv(b)
    x = x.A[deriv]
    m = x * rate ** deriv * factorial(deriv)

    # pad the signal at the extremes with
    # values taken from the signal itself
    first_vals = y[0] - np.abs(y[1:half_window + 1][::-1] - y[0])
    last_vals = y[-1] + np.abs(y[-half_window - 1:-1][::-1] - y[-1])
    y = np.concatenate((first_vals, y, last_vals))
    return np.convolve(m[::-1], y, mode='valid')


def plot_change(csv_name):
    raw_data = pd.read_csv(csv_name)
    time = raw_data['Time'][2:]
    left = raw_data['Left'][2:]
    right = raw_data['Right'][2:]
    difference = left - right
    difference_squared = difference.map(lambda x: x ** 2)
    assert len(difference_squared) == len(time)

    plt.figure()
    plt.plot(list(time), list(difference_squared))
    plt.savefig(os.path.splitext(csv_name)[0] + '_absolute_difference.pdf')

    plt.clf()
    y = savitzky_golay(difference_squared.values,  101, 3, deriv=0)
    plt.plot(list(time), list(y))
    plt.savefig(os.path.splitext(csv_name)[0] + '_smoothed_abs_diff.pdf')

    plt.clf()
    y = savitzky_golay(difference_squared.values,  101, 3, deriv=1)
    plt.plot(list(time), list(y))
    plt.savefig(os.path.splitext(csv_name)[0] + '_abs_diff_rate_of_change.pdf')
    plt.close()

plot_change('AG64 EMDR6 Spreadsheet1.csv')
