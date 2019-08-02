# -*- coding: utf-8 -*-
#
#
#  TheVirtualBrain-Scientific Package. This package holds all simulators, and 
# analysers necessary to run brain-simulations. You can use it stand alone or
# in conjunction with TheVirtualBrain-Framework Package. See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2017, Baycrest Centre for Geriatric Care ("Baycrest") and others
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#   CITATION:
# When using The Virtual Brain for scientific publications, please cite it as follows:
#
#   Paula Sanz Leon, Stuart A. Knock, M. Marmaduke Woodman, Lia Domide,
#   Jochen Mersmann, Anthony R. McIntosh, Viktor Jirsa (2013)
#       The Virtual Brain: a simulator of primate brain network dynamics.
#   Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)
#
#

"""
A collection of plotting functions used by simulator/demos

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>
.. moduleauthor:: Paula Sanz Leon <paula.sanz-leon@univ-amu.fr>
"""

from tvb.basic.logger.builder import get_logger
import time
import utils
import numpy
import numpy as np

LOG = get_logger(__name__)

# plotly import matplotlib altenetive and more friendly

import plotly.offline
import plotly.tools as tls

# ---------------------------------------------------------------------------
# -                  matplotlib based plotting functions
# --------------------------------------------------------------------------

import matplotlib.pyplot as pyplot
import matplotlib.colors
import matplotlib.ticker as ticker
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import colors

try:
    from mpl_toolkits.axes_grid import make_axes_locatable
    IMPORTED_MPL_TOOLKITS = True
except ImportError:
    IMPORTED_MPL_TOOLKITS = False
    LOG.error("You need mpl_toolkits")

def _blob(x, y, area, colour):
    """
    Draws a square-shaped blob with the given area (< 1) at
    the given coordinates.
    From : http://www.scipy.org/Cookbook/Matplotlib/HintonDiagrams
    """
    fig = pyplot.figure()
    hs = numpy.sqrt(area) / 2
    xcorners = numpy.array([x - hs, x + hs, x + hs, x - hs])
    ycorners = numpy.array([y - hs, y - hs, y + hs, y + hs])
    pyplot.fill(xcorners, ycorners, colour, edgecolor=colour)
    plotly_fig = tls.mpl_to_plotly(fig)
    plotly.offline.iplot(plotly_fig)

def longer_time_series(ts_int, tsr):

    """
    Create And Launch A TimeSeriesInteractive
    :param ts_int: import tvb.simulator.plot.timeseries_interactive as ts_int
    :param tsr: ime_series.TimeSeriesRegion()
    :return:
    """

    tsi = ts_int.TimeSeriesInteractive(time_series=tsr)
    tsi.configure()
    tsi.show()

def phase_plane_tool(ppi, epileptor):

    """
    Open the phase plane tool with the epileptor model
    :param ppi: from tvb.simulator.plot.phase_plane_interactive import PhasePlaneInteractive as ppi
    :param epileptor: epileptor = models.Epileptor(
    :return:
    """
    ppi_fig = ppi(model=epileptor)
    ppi_fig.show()

def epi_time_series(tavg, t):

    """
    Triggering a seizure by stimulation
    :param tavg: (np.max(tavg,0) - np.min(tavg,0 ))
    :param t: sim.run()
    :return:
    """

    # Plot raw time series
    fig = pyplot.figure(figsize=(10, 10))
    pyplot.plot(t[:], tavg[:, 0, :, 0] + numpy.r_[:76], 'r')
    pyplot.title("Epileptors time series")

    # Show them
    pyplot.show()
    plotly_fig = tls.mpl_to_plotly(fig)
    plotly.offline.iplot(plotly_fig)

def display_source_sensor(conn, sens_eeg, skin, sens_meg):
    """
    Display ROIs & M/EEG sensor positions

    :param conn:
    :param sens_eeg:
    :param skin:
    :param sens_meg:
    :return:
    """
    fig = pyplot.figure()
    ax = pyplot.subplot(111, projection='3d')

    # ROI centers as black circles
    x, y, z = conn.centres.T
    ax.plot(x, y, z, 'ko')

    # EEG sensors as blue x's
    x, y, z = sens_eeg.sensors_to_surface(skin).T
    ax.plot(x, y, z, 'bx')

    # Plot boundary surface
    x, y, z = skin.vertices.T
    ax.plot_trisurf(x, y, z, triangles=skin.triangles, alpha=0.1, edgecolor='none')

    # MEG sensors as red +'s
    x, y, z = sens_meg.locations.T
    ax.plot(x, y, z, 'r+')
    # Plot using plotly
    plotly_fig = tls.mpl_to_plotly(fig)
    plotly.offline.iplot(plotly_fig)

def compare_inte(raws, names, exp, t, r_):
    """
    Often it is difficult to know which is the best integration method
    for your simulation. TVB offers a handful of methods, with recently
    added variable order methods which allow one to safely choose higher
    time steps, as long as they remain smaller than the smallest time delay.

    :param raws:
    :param names:
    :param exp:
    :param t:
    :param r:
    :return:
    """
    n_raw = len(raws)
    fig = pyplot.figure(figsize=(15, 15))
    for i, (raw_i, name_i) in enumerate(zip(raws, names)):
        for j, (raw_j, name_j) in enumerate(zip(raws, names)):
            pyplot.subplot(n_raw, n_raw, i * n_raw + j + 1)
            if raw_i.shape[0] != t.shape[0] or raw_i.shape[0] != raw_j.shape[0]:
                continue
            if i == j:
                pyplot.plot(t, raw_i[:, 0, :, 0], 'k', alpha=0.1)
            else:
                pyplot.semilogy(t, (abs(raw_i - raw_j) / raw_i.ptp())[:, 0, :, 0], 'k', alpha=0.1)
                pyplot.ylim(exp(r_[-30, 0]))

            pyplot.grid(True)
            if i == 0:
                pyplot.title(name_j)
            if j == 0:
                pyplot.ylabel(name_i)

        if i == 0:
            euler_raw = raw
        else:
            raw = abs(raw - euler_raw) / euler_raw.ptp() * 100.0

    pyplot.tight_layout()
    plotly_fig = tls.mpl_to_plotly(fig)
    plotly.offline.iplot(plotly_fig)

def hinton_diagram(connectivity_weights, num, maxWeight=None):
    """
    Draws a Hinton diagram. This function temporarily disables matplotlib
    interactive mode if it is on, otherwise this takes forever.
    """
    weights_figure = pyplot.figure(num=num)
    height, width = connectivity_weights.shape

    if not maxWeight:
        maxWeight = 2 ** numpy.ceil(numpy.log(numpy.max(numpy.abs(connectivity_weights))) / numpy.log(2))

    # pyplot.fill(numpy.array([0,width,width,0]),numpy.array([0,0,height+0.5,height+0.5]),'gray')
    pyplot.axis('equal')
    weights_axes = weights_figure.gca()

    for x in range(width):
        for y in range(height):
            _x = x + 1
            _y = y + 1
            w = connectivity_weights[y, x]
            if w > 0:
                _blob(_x - 1., height - _y + 0.0, min(1, w / maxWeight), 'red')
            elif w < 0:
                _blob(_x - 1., height - _y + 0.0, min(1, -w / maxWeight), 'black')
    return weights_axes

    plotly_fig = tls.mpl_to_plotly(weights_figure)
    plotly.offline.iplot(plotly_fig)

def plot_connectivity(connectivity, num="weights", order_by=None, plot_hinton=False, plot_tracts=True):
    """
    A 2D plot for visualizing the Connectivity.weights matrix
    """

    def plot_with_weights(weights):
        """
        Connectivity normalization
        With significant variability between methods of obtaining structural connectivity,
        it is often useful to normalize, in one sense or another, the connectivity when
        comparing, for example, across subjects, or standardizing parameter ranges.

        :param weights: mode e.g region default none
        :output: 2d plot
        """
        conn = connectivity.Connectivity(load_default=True)
        conn.configure()
        conn.weights = weights
        plot_connectivity(conn, num="tract_mode", plot_tracts=False)

    labels = connectivity.region_labels
    plot_title = connectivity.__class__.__name__

    if order_by is None:
        order = numpy.arange(connectivity.number_of_regions)
    else:
        order = numpy.argsort(order_by)
        if order.shape[0] != connectivity.number_of_regions:
            LOG.error("Ordering vector doesn't have length number_of_regions")
            LOG.error("Check ordering length and that connectivity is configured")
            return

    # Assumes order is shape (number_of_regions, )
    order_rows = order[:, numpy.newaxis]
    order_columns = order_rows.T

    if plot_hinton:
        weights_axes = hinton_diagram(connectivity.weights[order_rows, order_columns], num)
    else:
        # weights matrix
        weights_figure = pyplot.figure()
        weights_axes = weights_figure.gca()
        wimg = weights_axes.matshow(connectivity.weights[order_rows, order_columns])
        weights_figure.colorbar(wimg)
        plotly_fig = tls.mpl_to_plotly(weights_figure)
        plotly.offline.iplot(plotly_fig)
    weights_axes.set_title(plot_title)

    if plot_tracts:
        # tract lengths matrix
        tracts_figure = pyplot.figure(num="tract-lengths")
        tracts_axes = tracts_figure.gca()
        timg = tracts_axes.matshow(connectivity.tract_lengths[order_rows, order_columns])
        tracts_axes.set_title(plot_title)
        tracts_figure.colorbar(timg)

    if labels is None:
        return
    weights_axes.set_yticks(numpy.arange(connectivity.number_of_regions))
    weights_axes.set_yticklabels(list(labels[order]), fontsize=8)

    weights_axes.set_xticks(numpy.arange(connectivity.number_of_regions))
    weights_axes.set_xticklabels(list(labels[order]), fontsize=8, rotation=90)

    if plot_tracts:
        tracts_axes.set_yticks(numpy.arange(connectivity.number_of_regions))
        tracts_axes.set_yticklabels(list(labels[order]), fontsize=8)

        tracts_axes.set_xticks(numpy.arange(connectivity.number_of_regions))
        tracts_axes.set_xticklabels(list(labels[order]), fontsize=8, rotation=90)

def plot_local_connectivity(cortex, cutoff=None):
    """
    Display the local connectivity function as a line plot. Four lines are
    plotted of the equations defining the LocalConnectivity:
        
        1) black, a 'high' resolution version evaluated out to a 'sufficiently
        large distance', ie, this is what you ideally want to represent;
        
        2) green, best case 'reality', based on shortest edge and cutoff 
        distance;
        
        3) red, worst case 'reality', based on longest edge and cutoff distance;
        
        4) blue, typical case 'reality', based on average edge length and cutoff
        distance.
    
    Usage, from demos directory, with tvb in your path ::
        
        import tvb.datatypes.surfaces as surfaces
        import plotting_tools
        cortex = surfaces.Cortex()
        plotting_tools.plot_local_connectivity(cortex, cutoff=60.)
        plotting_tools.pyplot.show()
        
    """

    dashes = ['--',  # : dashed line   -- blue
              '-.',  # : dash-dot line -- red
              ':',   # : dotted line   -- green
              '-']   # : solid line    -- black


    # If necessary, add a default LocalConnectivity to ``local_connectivity``.
    if cortex.local_connectivity is None:
        LOG.info("local_connectivity is None, adding default LocalConnectivity")
        cortex.local_connectivity = cortex.trait["local_connectivity"]

    if cutoff:
        cortex.local_connectivity.cutoff = cutoff

    # We need a cutoff distance to work from...
    if cortex.local_connectivity.cutoff is None:
        LOG.error("You need to provide a cutoff...")
        return

    cutoff = cortex.local_connectivity.cutoff
    cutoff_2 = 2.0 * cortex.local_connectivity.cutoff

    fig = pyplot.figure(num="Local Connectivity Cases")
    pyplot.title("Local Connectivity Cases")

    # ideally all these lines should overlap

    # What we want
    hi_res = 1024
    step = 2.0 * cutoff_2 / (hi_res - 1)
    hi_x = numpy.arange(-cutoff_2, cutoff_2 + step, step)
    pyplot.plot(hi_x, cortex.local_connectivity.equation.evaluate(numpy.abs(hi_x)), 'k',
                linestyle=dashes[-1], linewidth=3)

    # What we'll mostly get
    avg_res = 2 * int(cutoff / cortex.edge_length_mean)
    step = cutoff_2 / (avg_res - 1)
    avg_x = numpy.arange(-cutoff, cutoff + step, step)
    pyplot.plot(avg_x, cortex.local_connectivity.equation.evaluate(numpy.abs(avg_x)), 'b',
                linestyle=dashes[0], linewidth=3)

    # It can be this bad
    worst_res = 2 * int(cutoff / cortex.edge_length_max)
    step = cutoff_2 / (worst_res - 1)
    worst_x = numpy.arange(-cutoff, cutoff + step, step)
    pyplot.plot(worst_x, cortex.local_connectivity.equation.evaluate(numpy.abs(worst_x)), 'r',
                linestyle=dashes[1], linewidth=3)

    # This is as good as it gets...
    best_res = 2 * int(cutoff / cortex.edge_length_min)
    step = cutoff_2 / (best_res - 1)
    best_x = numpy.arange(-cutoff, cutoff + step, step)
    pyplot.plot(best_x, cortex.local_connectivity.equation.evaluate(numpy.abs(best_x)), 'g',
                linestyle=dashes[2], linewidth=3)

    # Plot the cutoff
    ymin, ymax = pyplot.ylim()
    pyplot.plot([-cutoff, -cutoff], [ymin, ymax], "k--")
    pyplot.plot([cutoff, cutoff], [ymin, ymax], "k--")

    pyplot.xlim([-cutoff_2, cutoff_2])
    pyplot.xlabel("Distance from focal point")
    pyplot.ylabel("Strength")
    pyplot.legend(("Theoretical", "Typical", "Worst", "Best", "Cutoff"))
    plotly_fig = tls.mpl_to_plotly(fig)
    plotly.offline.iplot(plotly_fig)

def temp_avg_timeseries(TAVG, EEG, nodes, tt):
    """
    Temporal Averaged time-series
    :param TAVG: numpy array
    :param EEG: numpy array
    :param tt: numpy array
    :return: output: 2D time Series
    """
    fig = pyplot.figure()
    pyplot.subplot(211)
    pyplot.plot(tt, TAVG[:, 0, nodes, 0])
    pyplot.title("Temporal Averaged time-series")
    pyplot.subplot(212)
    pyplot.plot(tt, EEG[:, 0, 60, 0], 'k')
    pyplot.title("EEG")
    pyplot.tight_layout()
    plotly_fig = tls.mpl_to_plotly(fig)
    plotly.offline.iplot(plotly_fig)

def plot_pattern(pattern_object):
    """
    pyplot in 2D the given X, over T.
    """
    fig = pyplot.figure(42)
    pyplot.subplot(221)
    pyplot.plot(pattern_object.spatial_pattern, "k*")
    pyplot.title("Space")
    # pyplot.plot(pattern_object.space, pattern_object.spatial_pattern, "k*")
    pyplot.subplot(223)
    pyplot.plot(pattern_object.time.T, pattern_object.temporal_pattern.T)
    pyplot.title("Time")
    pyplot.subplot(122)
    pyplot.imshow(pattern_object(), aspect="auto")
    pyplot.colorbar()
    pyplot.title("Stimulus")
    pyplot.xlabel("Time")
    pyplot.ylabel("Space")
    # plot on plotly
    plotly_fig = tls.mpl_to_plotly(fig)
    plotly.offline.iplot(plotly_fig)

def show_me_the_colours():
    """
    Create a plot of matplotlibs built-in "named" colours...
    """
    colours = matplotlib.colors.cnames.keys()
    number_of_colors = len(colours)
    colours_fig = pyplot.figure(num="Built-in colours")
    rows = int(numpy.ceil(numpy.sqrt(number_of_colors)))
    columns = int(numpy.floor(numpy.sqrt(number_of_colors)))
    for k in range(number_of_colors):
        ax = colours_fig.add_subplot(rows, columns, k)
        ax.set_yticklabels([])
        ax.set_xticklabels([])
        ax.set_axis_bgcolor(colours[k])
        ax.text(0.05, 0.5, colours[k])
        plotly_fig = tls.mpl_to_plotly(colours_fig)
        plotly.offline.iplot(plotly_fig)

def plot_matrix(mat, fig_name='plot_this_matrix', connectivity=None, binary_matrix=False):
    """
    An embellished matshow display
    """
    # NOTE: I could add more stuff in plot_connectivity, but I rather have
    # a dummy function for displaying a pretty matrix with the 
    # value of each element.

    fig, ax = pyplot.subplots(num=fig_name, figsize=(12,10))


    if binary_matrix:
        cmap = colors.ListedColormap(['black', 'white'])
        bounds=[0,1,2]
        norm = colors.BoundaryNorm(bounds, cmap.N)

        p = ax.pcolormesh(mat, cmap=cmap, norm=norm, edgecolors='k')
        ax.invert_yaxis()
        cbar = fig.colorbar(p, cmap=cmap, norm=norm, boundaries=bounds, ticks=[0.5, 1.5])
        cbar.ax.set_yticklabels(['no connections', 'connections'], fontsize=24)

    else:
        fig = pyplot.figure(num=fig_name)
        ax = fig.gca()
        res = ax.imshow(mat, cmap=pyplot.cm.coolwarm, interpolation='nearest')
        fig.colorbar(res)

    if connectivity is not None:
        order = numpy.arange(connectivity.number_of_regions)
        labels = connectivity.region_labels
        pyplot.xticks(numpy.arange(connectivity.number_of_regions)+0.5, list(labels[order]), fontsize=10, rotation=90)
        pyplot.yticks(numpy.arange(connectivity.number_of_regions)+0.5, list(labels[order]), fontsize=10)
    
    width  = mat.shape[0]
    height = mat.shape[1]
    plotly_fig = tls.mpl_to_plotly(fig)
    plotly.offline.iplot(plotly_fig)

def plot_3d_centres(xyz):
    """Plot 3D"""
    fig = pyplot.figure(1)
    fig.clf()
    ax = Axes3D(fig)
    ax.plot(xyz[:, 0], xyz[:, 1], xyz[:, 2], 'o', alpha=0.6)
    ax.set_xlim([min(xyz[:, 0]), max(xyz[:, 0])])
    ax.set_ylim([min(xyz[:, 1]), max(xyz[:, 1])])
    ax.set_zlim([min(xyz[:, 2]), max(xyz[:, 2])])
    ax.set_xlabel('x [mm]')
    ax.set_ylabel('y [mm]')
    ax.set_zlabel('z [mm]')
    plotly_fig = tls.mpl_to_plotly(fig)
    plotly.offline.iplot(plotly_fig)

def plot_tri_matrix(mat, figure=None, num='plot_part_of_this_matrix', size=None,
                        cmap=pyplot.cm.RdBu_r, colourbar=True,
                        color_anchor=None, node_labels=None, x_tick_rot=0, 
                        title=None):
    """Creates a lower-triangle of a square matrix. Very often found to display correlations or coherence.

    Parameters
    ----------

    mat          : square matrix

    node_labels  : list of strings with the labels to be applied to 
                   the nodes. Defaults to '0','1','2', etc.

    fig          : a matplotlib figure

    cmap         : a matplotlib colormap.

    title        : figure title (eg '$\alpha$')

    color_anchor : determines the clipping for the colormap. 
                   If None, the data min, max are used.
                   If 0, min and max of colormap correspond to max abs(mat)
                   If (a,b), min and max are set accordingly (a,b)

    Returns
    -------

    fig: a figure object

    """

    def channel_formatter(x, pos=None):
        thisidx = numpy.clip(int(x), 0, N - 1)
        return node_labels[thisidx]

    if figure is not None:
        fig = figure
    else :
        if num is None:
            fig = pyplot.figure()
        else:
            fig = pyplot.figure(num=num)

    if size is not None:
        fig.set_figwidth(size[0])
        fig.set_figheight(size[1])

    ax_im = fig.add_subplot(1, 1, 1)

    N = mat.shape[0]
     
    if colourbar:
        if IMPORTED_MPL_TOOLKITS:
            divider = make_axes_locatable(ax_im)
            ax_cb   = divider.new_vertical(size="10%", pad=0.1, pack_start=True)
            fig.add_axes(ax_cb)
        else:
            pass

    mat_copy = mat.copy()

    # Null the upper triangle, including the main diagonal.
    idx_null           = numpy.triu_indices(mat_copy.shape[0])
    mat_copy[idx_null] = numpy.nan

    # Min max values
    max_val = numpy.nanmax(mat_copy)
    min_val = numpy.nanmin(mat_copy)

    if color_anchor is None:
        color_min = min_val
        color_max = max_val
    elif color_anchor == 0:
        bound = max(abs(max_val), abs(min_val))
        color_min = -bound
        color_max =  bound
    else:
        color_min = color_anchor[0]
        color_max = color_anchor[1]

    # The call to imshow produces the matrix plot:
    im = ax_im.imshow(mat_copy, origin='upper', interpolation='nearest',
                      vmin=color_min, vmax=color_max, cmap=cmap)

    # Formatting:
    ax = ax_im
    ax.grid(True)
    # Label each of the cells with the row and the column:
    if node_labels is not None:
        for i in range(0, mat_copy.shape[0]):
            if i < (mat_copy.shape[0] - 1):
                ax.text(i - 0.3, i, node_labels[i], rotation=x_tick_rot)
            if i > 0:
                ax.text(-1, i + 0.3, node_labels[i],
                        horizontalalignment='right')

        ax.set_axis_off()
        ax.set_xticks(numpy.arange(N))
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(channel_formatter))
        fig.autofmt_xdate(rotation=x_tick_rot)
        ax.set_yticks(numpy.arange(N))
        ax.set_yticklabels(node_labels)
        ax.set_ybound([-0.5, N - 0.5])
        ax.set_xbound([-0.5, N - 1.5])

    # Make the tick-marks invisible:
    for line in ax.xaxis.get_ticklines():
        line.set_markeredgewidth(0)

    for line in ax.yaxis.get_ticklines():
        line.set_markeredgewidth(0)

    ax.set_axis_off()

    if title is not None:
        ax.set_title(title)

    if colourbar:
        # Set the ticks - if 0 is in the interval of values, set that, as well
        # as the min, max values:
        if min_val < 0:
            ticks = [color_min, min_val, 0, max_val, color_max]
        # set the min, mid and  max values:
        else:
            ticks = [color_min, min_val, (color_max- color_min)/2., max_val, color_max]


        # colourbar:
        if IMPORTED_MPL_TOOLKITS:
            cb = fig.colorbar(im, cax=ax_cb, orientation='horizontal',
                              cmap=cmap,
                              norm=im.norm,
                              boundaries=numpy.linspace(color_min, color_max, 256),
                              ticks=ticks,
                              format='%.2f')

        else:
            # the colourbar will be wider than the matrix
            cb = fig.colorbar(im, orientation='horizontal',
                              cmap=cmap,
                              norm=im.norm,
                              boundaries=numpy.linspace(color_min, color_max, 256),
                              ticks=ticks,
                              format='%.2f')

    fig.sca(ax)
    plotly_fig = tls.mpl_to_plotly(fig)
    plotly.offline.iplot(plotly_fig)

    return fig

def plot_roi_corr_map(reg_name, conn, t, y, corrcoef):
    """
    Seed-region correlation maps

    A common visualization of FC specific to a given is to pull out its
    row of the FC matrix and plot a colormap on the anatomy. We can do this
    will the simulated functional connectivity to identify which regions are
    highly coordinated with the seed region.

    :param reg_name: Reg/plot name
    :param conn: connectivity e.g conn = connectivity.Connectivity(load_default=True)
    :return: Output: 3d plot of the various angles of human brain
    """
    cs = []
    for i in range(int(t[-1] / 1e3)):
        cs.append(corrcoef(y[(t > (i * 1e3)) * (t < (1e3 * (i + 1)))].T))
    cs = numpy.array(cs)
    cs.shape
    roi = numpy.find(conn.ordered_labels==reg_name)[0]
    cs_m = cs[2:].mean(axis=0)
    rm = utils.cortex.region_mapping
    utils.multiview(cs_m[roi][rm], shaded=False, suptitle=reg_name, figsize=(10, 5))

def plot_brain_network_model(tavg_time, tavg_data, ):
    """

    """
    TAVG = numpy.array(tavg_data)
    tavg_time = numpy.array(tavg_time)
    t_interval = numpy.arange(100)

    # Plot raw time series
    fig1 = pyplot.figure(1)
    pyplot.plot(tavg_time[t_interval], TAVG[t_interval, 0, :, 0], 'k', alpha=0.05)
    pyplot.plot(tavg_time[t_interval], TAVG[t_interval, 0, :, 0].mean(axis=1), 'k', linewidth=3)
    pyplot.title("Temporal average -- State variable V")
    plotly_fig = tls.mpl_to_plotly(fig1)
    plotly.offline.iplot(plotly_fig)

    fig2 = pyplot.figure(2)
    pyplot.plot(tavg_time[t_interval], TAVG[t_interval, 1, :, 0], 'b', alpha=0.05)
    pyplot.plot(tavg_time[t_interval], TAVG[t_interval, 1, :, 0].mean(axis=1), 'b', linewidth=3)
    pyplot.title("Temporal average -- State variable W")
    plotly_fig = tls.mpl_to_plotly(fig2)
    plotly.offline.iplot(plotly_fig)

    fig3 = pyplot.figure(3)
    pyplot.plot(tavg_time[t_interval], TAVG[t_interval, 2, :, 0], 'r', alpha=0.05)
    pyplot.plot(tavg_time[t_interval], TAVG[t_interval, 2, :, 0].mean(axis=1), 'r', linewidth=3)
    pyplot.title("Temporal average -- State variable Z")
    pyplot.xlabel('time [ms]', fontsize=24)
    plotly_fig = tls.mpl_to_plotly(fig3)
    plotly.offline.iplot(plotly_fig)

def sim_sum_eeg(eeg, meg, seeg):
    """
    Cortical surface with subcortical regions,
    sEEG, EEG & MEG, using a stochastic integration.
    """
    fig = pyplot.figure()

    for i, mon in enumerate((eeg, meg, seeg)):
        pyplot.subplot(3, 1, i + 1)
        time, data = mon
        pyplot.plot(time, data[:, 0, :, 0], 'k', alpha=0.1)
        pyplot.ylabel(['EEG', 'MEG', 'sEEG'][i])

    pyplot.tight_layout()
    plotly_fig = tls.mpl_to_plotly(fig)
    plotly.offline.iplot(plotly_fig)

def reg_red_wong_wang(colorbar, conn, imagesc, np2m):
    """
    perform a simulation with the reduced Wong-Wang model,
    using the default connectivity.
    :return:
    """
    fig = pyplot.figure('Position', [500, 500, 1000, 400])
    pyplot.subplot(121, imagesc(np2m(conn.weights)), colorbar, pyplot.title('Weights'))
    pyplot.subplot(122, imagesc(np2m(conn.tract_lengths)), colorbar)
    pyplot.title('Tract Lengths (mm)')
    plotly_fig = tls.mpl_to_plotly(fig)
    plotly.offline.iplot(plotly_fig)

def matlab_two_ep_sim(gca, squeeze, signal):
    """
    erform a simulation with two Epileptors.
    :return:
    """
    fig = pyplot.figure()

    pyplot.subplot(311)
    pyplot.plot(time, squeeze(signal(1, ':', 1, ':')), 'k')
    pyplot.ylabel('x2(t - x1(t)')
    pyplot.set(gca, 'XTickLabel', {})

    pyplot.title('Two Epileptors')

    # plot high-pass filtered LFP
    pyplot.subplot(312)
    [b, a] = buffer(3, 2/2000*5.0, 'high')
    hpf = filter(b, a, squeeze(signal(1,':', 1,':')))
    pyplot.plot(time, hpf(':',1),'k')
    pyplot.plot(time, hpf(':', 2), 'k')
    pyplot.set(gca, 'XTickLabel', {})
    pyplot.ylabel('HPF LFP')

    pyplot.subplot(313)
    pyplot.plot(time, squeeze(signal(1,':', 2,':')), 'k')
    pyplot.ylabel('Z(t)')
    pyplot.xlabel('Time (ms)')
    plotly_fig = tls.mpl_to_plotly(fig)
    plotly.offline.iplot(plotly_fig)

def region_simulate(raw_data, tavg_data, raw_time, tavg_time):
    """
    presents the basic anatomy of a region simulation using
    The Virtual Brain's (TVB's) scripting interface.
    :return:
    """
    # Make the lists numpy.arrays for easier use.
    RAW = numpy.array(raw_data)
    TAVG = numpy.array(tavg_data)

    # Plot raw time series
    fig = pyplot.figure(1)
    pyplot.plot(raw_time, RAW[:, 0, :, 0])
    pyplot.title("Raw -- State variable 0")

    # Plot temporally averaged time series
    pyplot.figure(2)
    pyplot.plot(tavg_time, TAVG[:, 0, :, 0])
    pyplot.title("Temporal average")

    # Show them
    pyplot.show()
    plotly_fig = tls.mpl_to_plotly(fig)
    plotly.offline.iplot(plotly_fig)

def centres_cubic(self, number_of_regions=4, max_radius=42., flat=False):
    """
    The nodes are positioined in a 3D grid inside the cube centred at the origin and
    with edges parallel to the axes, with an edge length of 2*max_radius.

    """

    # To cartesian coordinates
    x = numpy.linspace(-max_radius, max_radius, number_of_regions)
    y = numpy.linspace(-max_radius, max_radius, number_of_regions)

    if flat:
        z = numpy.zeros(number_of_regions)
    else:
        z = numpy.linspace(-max_radius, max_radius, number_of_regions)

    self.centres = numpy.array([x, y, z]).T

def three_d_dviewer():
    """Viewing 3D Volumetric Data With Matplotlib"""
    def remove_keymap_conflicts(new_keys_set):
        for prop in pyplot.rcParams:
            if prop.startswith('keymap.'):
                keys = pyplot.rcParams[prop]
                remove_list = set(keys) & new_keys_set
                for key in remove_list:
                    keys.remove(key)

    def multi_slice_viewer(volume):
        remove_keymap_conflicts({'j', 'k'})
        fig, ax = pyplot.subplots()
        ax.volume = volume
        ax.index = volume.shape[0] // 2
        ax.imshow(volume[ax.index])
        fig.canvas.mpl_connect('key_press_event', process_key)

    def process_key(event):
        fig = event.canvas.figure
        ax = fig.axes[0]
        if event.key == 'j':
            previous_slice(ax)
        elif event.key == 'k':
            next_slice(ax)
        fig.canvas.draw()

    def previous_slice(ax):
        volume = ax.volume
        ax.index = (ax.index - 1) % volume.shape[0]  # wrap around using %
        ax.images[0].set_array(volume[ax.index])

    def next_slice(ax):
        volume = ax.volume
        ax.index = (ax.index + 1) % volume.shape[0]
        ax.images[0].set_array(volume[ax.index])

def plot_fast_kde(x, sp, y, kern_nx = None, kern_ny = None, gridsize=(500, 500),
             extents=None, nocorrelation=False, weights=None, norm = True, pdf=False, **kwargs):
    """
    A faster gaussian kernel density estimate (KDE).  Intended for
    computing the KDE on a regular grid (different use case than
    scipy's original scipy.stats.kde.gaussian_kde()).  

    Author: Joe Kington
    License:  MIT License <http://www.opensource.org/licenses/mit-license.php>

    Performs a gaussian kernel density estimate over a regular grid using a
    convolution of the gaussian kernel with a 2D histogram of the data.

    This function is typically several orders of magnitude faster than 
    scipy.stats.kde.gaussian_kde for large (>1e7) numbers of points and 
    produces an essentially identical result.

    **Input**:
    
        *x*: array
            The x-coords of the input data points
        
        *y*: array
            The y-coords of the input data points
        
        *kern_nx*: float 
            size (in units of *x*) of the kernel

        *kern_ny*: float
            size (in units of *y*) of the kernel

        *gridsize*: (Nx , Ny) tuple (default: 500x500) 
            Size of the output grid
                    
        *extents*: (default: extent of input data) A (xmin, xmax, ymin, ymax)
            tuple of the extents of output grid

        *nocorrelation*: (default: False) If True, the correlation between the
            x and y coords will be ignored when preforming the KDE.
        
        *weights*: (default: None) An array of the same shape as x & y that 
            weighs each sample (x_i, y_i) by each value in weights (w_i).
            Defaults to an array of ones the same size as x & y.
            
        *norm*: boolean (default: False) 
            If False, the output is only corrected for the kernel. If True,
            the result is normalized such that the integral over the area 
            yields 1. 

    **Output**:
        A gridded 2D kernel density estimate of the input points. 
    """
   
    # ------------------------------- Setup ------------------------------------------
    x, y = numpy.asarray(x), numpy.asarray(y)
    x, y = numpy.squeeze(x), numpy.squeeze(y)
    
    if x.size != y.size:
        raise ValueError('Input x & y arrays must be the same size!')

    nx, ny = gridsize
    n = x.size

    if weights is None:
        # Default: Weight all points equally
        weights = numpy.ones(n)
    else:
        weights = numpy.squeeze(numpy.asarray(weights))
        if weights.size != x.size:
            raise ValueError('Input weights must be an array of the same size'
                    ' as input x & y arrays!')

    # Default extents are the extent of the data
    if extents is None:
        xmin, xmax = x.min(), x.max()
        ymin, ymax = y.min(), y.max()
    else:
        xmin, xmax, ymin, ymax = map(float, extents)
        
    dx = (xmax - xmin) / (nx - 1)
    dy = (ymax - ymin) / (ny - 1)

    # ---- Preliminary Calculations -------------------------------------------

    # First convert x & y over to pixel coordinates
    # (Avoiding np.digitize due to excessive memory usage!)
    xyi = numpy.vstack((x,y)).T
    xyi -= [xmin, ymin]
    xyi /= [dx, dy]
    xyi = numpy.floor(xyi, xyi).T

    # Next, make a 2D histogram of x & y
    # Avoiding np.histogram2d due to excessive memory usage with many points
    grid = sp.sparse.coo_matrix((weights, xyi), shape=(nx, ny)).toarray()

    # Calculate the covariance matrix (in pixel coords)
    cov = numpy.cov(xyi)

    if nocorrelation:
        cov[1,0] = 0
        cov[0,1] = 0

    # Scaling factor for bandwidth
    scotts_factor = numpy.power(n, -1.0 / 6) # For 2D

    #---- Make the gaussian kernel -------------------------------------------

    # First, determine how big the kernel needs to be
    std_devs = numpy.diag(numpy.sqrt(cov))

    if kern_nx is None or kern_ny is None: 
        kern_nx, kern_ny = numpy.round(scotts_factor * 2 * numpy.pi * std_devs)
    
    else: 
        kern_nx = numpy.round(kern_nx / dx)
        kern_ny = numpy.round(kern_ny / dy)

    # Determine the bandwidth to use for the gaussian kernel
    inv_cov = numpy.linalg.inv(cov * scotts_factor**2) 

    # x & y (pixel) coords of the kernel grid, with <x,y> = <0,0> in center
    xx = numpy.arange(kern_nx, dtype=numpy.float) - kern_nx / 2.0
    yy = numpy.arange(kern_ny, dtype=numpy.float) - kern_ny / 2.0
    xx, yy = numpy.meshgrid(xx, yy)

    # Then evaluate the gaussian function on the kernel grid
    kernel = numpy.vstack((xx.flatten(), yy.flatten()))
    kernel = numpy.dot(inv_cov, kernel) * kernel 
    kernel = numpy.sum(kernel, axis=0) / 2.0 
    kernel = numpy.exp(-kernel) 
    kernel = kernel.reshape((kern_ny, kern_nx))

    #---- Produce the kernel density estimate --------------------------------

    # Convolve the gaussian kernel with the 2D histogram, producing a gaussian
    # kernel density estimate on a regular grid
    grid = sp.signal.convolve2d(grid, kernel, mode='same', boundary='fill').T

    # Normalization factor to divide result by so that units are in the same
    # units as scipy.stats.kde.gaussian_kde's output.  
    norm_factor = 2 * numpy.pi * cov * scotts_factor**2
    norm_factor = numpy.linalg.det(norm_factor)
    norm_factor = numpy.sqrt(norm_factor)
    
    if norm : 
        norm_factor *= n * dx * dy
    #  --------------------- Produce pdf--------------------------------

    if pdf:
        norm_factor, _ = sp.integrate.nquad(grid, [[xmin, xmax], [ymin, ymax]])

    # Normalize the result
    grid /= norm_factor

    return grid

if __name__ == '__main__':
    # Do some stuff that tests or makes use of this module... 
    pass

##- EoF -##