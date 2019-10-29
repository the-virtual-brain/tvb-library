# -*- coding: utf-8 -*-
#
# Some math tools
#
#

import numpy as np
from tvb.basic.logger.builder import get_logger
from tvb.simulator.plot.config import CONFIGURED
from tvb.simulator.plot.utils.data_structures_utils import is_integer

LOG = get_logger(__name__)


def normalize_weights(weights, percentile=CONFIGURED.calcul.WEIGHTS_NORM_PERCENT, remove_diagonal=True, ceil=1.0):
    # Create the normalized connectivity weights:
    if len(weights) > 0:
        normalized_w = np.array(weights)
        if remove_diagonal:
            # Remove diagonal elements
            n_regions = normalized_w.shape[0]
            normalized_w *= (1.0 - np.eye(n_regions))
        # Normalize with the 95th percentile
        normalized_w = np.array(normalized_w / np.percentile(normalized_w, percentile))
        if ceil:
            if ceil is True:
                ceil = 1.0
            normalized_w[normalized_w > ceil] = ceil
        return normalized_w
    else:
        return np.array([])


def compute_in_degree(weights):
    return np.expand_dims(np.sum(weights, axis=1), 1).T


def get_greater_values_array_inds(values, n_vals=1):
    return np.argsort(values)[::-1][:n_vals]


def select_greater_values_array_inds(values, threshold=None, percentile=None, nvals=None, verbose=False):
    if threshold is None and percentile is not None:
        threshold = np.percentile(values, percentile)
    if threshold is not None:
        return np.where(values > threshold)[0]
    else:
        if is_integer(nvals):
            return get_greater_values_array_inds(values, nvals)
        if verbose:
            LOG.warning("Switching to curve elbow point method since threshold=" + str(threshold))
        elbow_point = curve_elbow_point(values)
        return get_greater_values_array_inds(values, elbow_point)


def curve_elbow_point(vals, interactive=CONFIGURED.calcul.INTERACTIVE_ELBOW_POINT):
    # Solution found in
    # https://www.analyticbridge.datasciencecentral.com/profiles/blogs/identifying-the-number-of-clusters-finally-a-solution
    vals = np.array(vals).flatten()
    if np.any(vals[0:-1] - vals[1:] < 0):
        vals = np.sort(vals)
        vals = vals[::-1]
    cumsum_vals = np.cumsum(vals)
    grad = np.gradient(np.gradient(np.gradient(cumsum_vals)))
    elbow = np.argmax(grad)
    # alternatively:
    # dif = np.diff(np.diff(np.diff(cumsum_vals)))
    # elbow = np.argmax(dif) + 2
    if interactive:
        import matplotlib
        matplotlib.use(CONFIGURED.figures.MATPLOTLIB_BACKEND)
        from matplotlib import pyplot
        pyplot.ion()
        fig, ax = pyplot.subplots()
        xdata = list(range(len(vals)))
        lines = [ax.plot(xdata, cumsum_vals, 'g*', picker=None, label="values' cumulative sum")[0],
                 ax.plot(xdata, vals, 'bo', picker=None, label="values in descending order")[0],
                 ax.plot(elbow, vals[elbow], "rd",
                         label="suggested elbow point (maximum of third central difference)")[0],
                 ax.plot(elbow, cumsum_vals[elbow], "rd")[0]]
        pyplot.legend(handles=lines[:2])

        class MyClickableLines(object):

            def __init__(self, figure_no, axe, lines_list):
                self.x = None
                # self.y = None
                self.ax = axe
                title = "Mouse lef-click please to select the elbow point..." + \
                        "\n...or click ENTER to continue accepting our automatic choice in red..."
                self.ax.set_title(title)
                self.lines = lines_list
                self.fig = figure_no

            def event_loop(self):
                self.fig.canvas.mpl_connect('button_press_event', self.onclick)
                self.fig.canvas.mpl_connect('key_press_event', self.onkey)
                self.fig.canvas.draw_idle()
                self.fig.canvas.start_event_loop(timeout=-1)
                return

            def onkey(self, event):
                if event.key == "enter":
                    self.fig.canvas.stop_event_loop()
                return

            def onclick(self, event):
                if event.inaxes != self.lines[0].axes:
                    return
                dist = np.sqrt((self.lines[0].get_xdata() - event.xdata) ** 2.0)
                # + (self.lines[0].get_ydata() - event.ydata) ** 2.)
                self.x = np.argmin(dist)
                self.fig.canvas.stop_event_loop()
                return

        click_point = MyClickableLines(fig, ax, lines)
        click_point.event_loop()
        if click_point.x is not None:
            elbow = click_point.x
            LOG.info("\nmanual selection: " + str(elbow))
        else:
            LOG.info("\nautomatic selection: " + str(elbow))
        return elbow
    else:
        return elbow
