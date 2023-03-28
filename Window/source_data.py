from random import gauss, randint, uniform, seed
import math
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# MACRO-PARAMETERS
FREQUENCY = 3  # improves band pass filter resolution (=> better signal data)
COUNTS = 200  # also used in signal constructing. I've separated those parameters
# to increase resolution in frequency domain. Not sure if it worked.
ALL_COUNTS = FREQUENCY * COUNTS
SEED = 1  # parameter to initialize random numbers generator. This controlling random factor is used in constructing
# 'random' geological area reflectivity
EXCEPTION_COLOR = '\033[1;35m'


# SIGNAL COMPONENTS CONSTRUCTORS

def geo_reflect(positions, values):
    """Returns one signal - geological reflectivity
    Geological reflectivity - signal with few pics at given positions.
    Values in those positions should be less then 1 by absolute value"""
    reflectivity = np.zeros(ALL_COUNTS)
    for k, i in enumerate(positions):
        try:
            reflectivity[i] = values[k]
        except IndexError:  # enables shift geo_reflectivity how we want
            print("{0} Some picks of geo_reflectivity wasn't recorded."
                  " Index {1} out of range {2}".format(EXCEPTION_COLOR, i, ALL_COUNTS))
            continue
    return reflectivity


def add_noise(ar, math_exp=0, stand_dev=0.1):
    """ Adds gauss noise for given array (signal/trace). """
    for i in range(len(ar)):
        noise = gauss(mu=math_exp, sigma=stand_dev)
        ar[i] = ar[i] + noise
    return None


def band_pass_filter(w_min, w_max, show=False, crop=False):
    """ Band-pass filter in time axis."""
    max_sample = COUNTS
    freq = FREQUENCY
    # counts = range(-int(max_sample / 2), math.ceil(max_sample / 2))
    if show:
        w = np.linspace(w_min, w_max, num=max_sample)
        W_axis = np.linspace(0, w_min, num=max_sample).tolist() + w.tolist() + np.linspace(w_max, np.pi,
                                                                                           num=max_sample).tolist()
        A_axis = [0 for x in range(len(w))] + [1 for x in range(len(w))] + [0 for x in range(len(w))]
        fig = plt.figure()
        fig.set_figheight(13)
        fig.set_figwidth(13)
        ax = fig.add_subplot(111)
        ax.plot(W_axis, A_axis)
        fig.suptitle("Полосовой фильтр", fontsize=20, fontweight='bold')
        ax.set_xlabel('w, Гц', fontsize=13, style="italic")
        ax.set_ylabel('|A(w)|', fontsize=13, style="italic")
        plt.subplots_adjust(left=0.1,
                            bottom=0.1,
                            right=0.9,
                            top=0.88,
                            wspace=0.4,
                            hspace=0.4)
    if crop:
        counts = np.linspace(0, math.ceil(max_sample / 2), num=max_sample * freq)
    else:
        counts = np.linspace(-int(max_sample / 2), math.ceil(max_sample / 2), num=max_sample * freq)
    hamming_window = []
    if w_min * w_max > 0 and abs(w_max) <= np.pi and abs(w_min) <= np.pi:  # Two rectangles
        for t in counts:
            f_t = np.sign(w_min) * (w_max * np.sinc(w_max * t / np.pi) - w_min * np.sinc(w_min * t / np.pi)) / np.pi
            hamming_window.append(f_t * (0.53836 + 0.46164 * np.cos(2 * np.pi * t / len(counts))))
        norma = max(hamming_window)
        hamming_window = [value / norma for value in hamming_window]
        return hamming_window
    else:
        print("Error!!!")
        return None


def dirac_function(length, value):
    # IT'S USELESS. DELETE
    """Delta function with customable amplitude"""
    delta = np.zeros(length)
    delta[int(length / 2) - 1] = value
    return delta


def wave(band_pass_filter, amplitude=1, dirac_function=None):
    """Returns one signal - band pass filter in time domain, scaled by variable 'amplitude'"""
    CONV_MODE = 'same'
    if dirac_function is not None:
        return np.convolve(band_pass_filter, dirac_function, mode=CONV_MODE)
    else:
        return np.multiply(band_pass_filter, amplitude)


def signal(forming_wave, reflection, noise=None):
    CONV_MODE = 'same'
    out_signal = np.convolve(forming_wave, reflection, mode=CONV_MODE)
    if noise is not None:
        if not (isinstance(noise, float) or isinstance(noise, int)):
            raise ValueError('Standard deviation (noise=) should be numerical')
        add_noise(out_signal, stand_dev=noise)
    return out_signal


# SEISMIC IMAGES CONSTRUCTORS

def area_reflectivity(geo_layers_amount, traces_amount, shift=0, fluctuation=False):
    """Constructor for geophysical visualization of area. Crucial method for testing.
    :return list of reflectivity traces in each seismic source
    """
    seed(SEED)  # make random generator fixed (stationary)
    areal_reflect = []
    picks_positions = [randint(0, ALL_COUNTS) for _ in range(geo_layers_amount)]
    picks_values = [uniform(-1, 1) for _ in range(geo_layers_amount)]
    for i in range(traces_amount):
        if shift != 0:
            picks_positions = np.add(picks_positions, shift * i)
        recordings = geo_reflect(picks_positions, picks_values)
        areal_reflect.append(recordings)
    seed(datetime.now())  # move random numbers generator back to loose state
    return areal_reflect



def seismic_image(forming_geo_area, forming_wave, stand_div=None):
    """Builds """
    image = []
    for recorded_reflectivity in forming_geo_area:
        pure_signal = signal(forming_wave, recorded_reflectivity, noise=stand_div)
        image.append(pure_signal)
    return image


# def sort(*seismogramms):
#     sorted_list = []
#     traces_same_position = []
#     for i in range(len(seismogramms[0])):
#         for ogt in seismogramms:
#             traces_same_position.append(ogt[i])
#         sorted_list.append(traces_same_position)
#         traces_same_position = []
#     return sorted_list



# def OPS(*seismogramms):
#     """Makes optimal OGT"""
#     sorted_traces = sort(*seismogramms)
#     optimal_OGT = []
#     for traces in sorted_traces:
#         optimal_trace = optis(traces)
#         optimal_OGT.append(optimal_trace)
#     return optimal_OGT
#
#
# def SS(*seismogramms):
#     """Just straight sum"""
#     sorted_traces = sort(*seismogramms)
#     straight_OGT = []
#     for traces in sorted_traces:
#         straight_trace = straight_sum(*traces)
#         straight_OGT.append(straight_trace)
#     return straight_OGT
