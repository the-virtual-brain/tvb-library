# -*- coding: utf-8 -*-
#
#
#  TheVirtualBrain-Scientific Package. This package holds all simulators, and 
# analysers necessary to run brain-simulations. You can use it stand alone or
# in conjunction with TheVirtualBrain-Framework Package. See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2013, Baycrest Centre for Geriatric Care ("Baycrest")
#
# This program is free software; you can redistribute it and/or modify it under 
# the terms of the GNU General Public License version 2 as published by the Free
# Software Foundation. This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details. You should have received a copy of the GNU General 
# Public License along with this program; if not, you can download it here
# http://www.gnu.org/licenses/old-licenses/gpl-2.0
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

import an usage for MAYAVI based plots should look like::
    
    from tvb.simulator.plot.tools import *
    
    if IMPORTED_MAYAVI:
        plt = plot_function(...)

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>
.. moduleauthor:: Paula Sanz Leon <paula.sanz-leon@univ-amu.fr>
"""

import numpy
import networkx as nx
from tvb.basic.logger.builder import get_logger

LOG = get_logger(__name__)


##----------------------------------------------------------------------------##
##-                  matplotlib based plotting functions                     -##
##---------------------------------------------------------------------------cd-##

import matplotlib as mpl
import matplotlib.pyplot as pyplot
import matplotlib.colors
import matplotlib.ticker as ticker
import matplotlib.colors as colors
from mpl_toolkits.axes_grid import make_axes_locatable  


def _blob(x, y, area, colour):
    """
    Draws a square-shaped blob with the given area (< 1) at
    the given coordinates.
    From : http://www.scipy.org/Cookbook/Matplotlib/HintonDiagrams
    """
    hs = numpy.sqrt(area) / 2
    xcorners = numpy.array([x - hs, x + hs, x + hs, x - hs])
    ycorners = numpy.array([y - hs, y - hs, y + hs, y + hs])
    pyplot.fill(xcorners, ycorners, colour, edgecolor=colour)



def hinton_diagram(connectivity_weights, num, maxWeight=None):
    """
    Draws a Hinton diagram. This function temporarily disables matplotlib
    interactive mode if it is on, otherwise this takes forever.
    """
    weights_figure = pyplot.figure(num=num)
    height, width = connectivity_weights.shape

    if not maxWeight:
        maxWeight = 2 ** numpy.ceil(numpy.log(numpy.max(numpy.abs(connectivity_weights))) / numpy.log(2))

    #pyplot.fill(numpy.array([0,width,width,0]),numpy.array([0,0,height+0.5,height+0.5]),'gray')
    pyplot.axis('equal')
    weights_axes = weights_figure.gca()

    for x in xrange(width):
        for y in xrange(height):
            _x = x + 1
            _y = y + 1
            w = connectivity_weights[y, x]
            if w > 0:
                _blob(_x - 1., height - _y + 0.0, min(1, w / maxWeight), 'red')
            elif w < 0:
                _blob(_x - 1., height - _y + 0.0, min(1, -w / maxWeight), 'black')
    return weights_axes



def plot_connectivity(connectivity, num="weights", order_by=None, plot_hinton=False, plot_tracts=True):
    """
    A 2D plot for visualizing the Connectivity.weights matrix
    """
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


    #If necessary, add a default LocalConnectivity to ``local_connectivity``.
    if cortex.local_connectivity is None:
        LOG.info("local_connectivity is None, adding default LocalConnectivity")
        cortex.local_connectivity = cortex.trait["local_connectivity"]

    if cutoff:
        cortex.local_connectivity.cutoff = cutoff

    #We need a cutoff distance to work from...
    if cortex.local_connectivity.cutoff is None:
        LOG.error("You need to provide a cutoff...")
        return

    cutoff = cortex.local_connectivity.cutoff
    cutoff_2 = 2.0 * cortex.local_connectivity.cutoff

    pyplot.figure(num="Local Connectivity Cases")
    pyplot.title("Local Connectivity Cases")

    # ideally all these lines should overlap

    #What we want
    hi_res = 1024
    step = 2.0 * cutoff_2 / (hi_res - 1)
    hi_x = numpy.arange(-cutoff_2, cutoff_2 + step, step)
    cortex.local_connectivity.equation.pattern = numpy.abs(hi_x)
    pyplot.plot(hi_x, cortex.local_connectivity.equation.pattern, 'k',
                linestyle=dashes[-1], linewidth=3)

    #What we'll mostly get
    avg_res = 2 * int(cutoff / cortex.edge_length_mean)
    step = cutoff_2 / (avg_res - 1)
    avg_x = numpy.arange(-cutoff, cutoff + step, step)
    cortex.local_connectivity.equation.pattern = numpy.abs(avg_x)
    pyplot.plot(avg_x, cortex.local_connectivity.equation.pattern, 'b',
                linestyle=dashes[0], linewidth=3)

    #It can be this bad
    worst_res = 2 * int(cutoff / cortex.edge_length_max)
    step = cutoff_2 / (worst_res - 1)
    worst_x = numpy.arange(-cutoff, cutoff + step, step)
    cortex.local_connectivity.equation.pattern = numpy.abs(worst_x)
    pyplot.plot(worst_x, cortex.local_connectivity.equation.pattern, 'r',
                linestyle=dashes[1], linewidth=3)

    #This is as good as it gets...
    best_res = 2 * int(cutoff / cortex.edge_length_min)
    step = cutoff_2 / (best_res - 1)
    best_x = numpy.arange(-cutoff, cutoff + step, step)
    cortex.local_connectivity.equation.pattern = numpy.abs(best_x)
    pyplot.plot(best_x, cortex.local_connectivity.equation.pattern, 'g',
                linestyle=dashes[2], linewidth=3)

    #Plot the cutoff
    ymin, ymax = pyplot.ylim()
    pyplot.plot([-cutoff, -cutoff], [ymin, ymax], "k--")
    pyplot.plot([cutoff, cutoff], [ymin, ymax], "k--")

    pyplot.xlim([-cutoff_2, cutoff_2])
    pyplot.xlabel("Distance from focal point")
    pyplot.ylabel("Strength")
    pyplot.legend(("Theoretical", "Typical", "Worst", "Best", "Cutoff"))

    # set the linewidth of the first legend object
    #leg.legendHandles[0].set_linewidth(6.0)
    #leg.legendHandles[1].set_linewidth(6.0)
    #leg.legendHandles[2].set_linewidth(6.0)
    #leg.legendHandles[3].set_linewidth(6.0)



def plot_pattern(pattern_object):
    """
    pyplot in 2D the given X, over T.
    """
    pyplot.figure(42)
    pyplot.subplot(221)
    pyplot.plot(pattern_object.spatial_pattern, "k*")
    pyplot.title("Space")
    #pyplot.plot(pattern_object.space, pattern_object.spatial_pattern, "k*")
    pyplot.subplot(223)
    pyplot.plot(pattern_object.time.T, pattern_object.temporal_pattern.T)
    pyplot.title("Time")
    pyplot.subplot(122)
    pyplot.imshow(pattern_object(), aspect="auto")
    pyplot.colorbar()
    pyplot.title("Stimulus")
    pyplot.xlabel("Time")
    pyplot.ylabel("Space")
    #pyplot.show()



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


def plot_tri_matrix(mat, num='plot_part_of_this_matrix', size=None, 
                        cmap=pyplot.cm.RdBu_r, colourbar=True,
                        color_anchor=None, node_labels=None, x_tick_rot=0, 
                        title=None):
    r"""Creates a lower-triangle of a square matrix. Very often found to display correlations or coherence.

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

    if num is None:
        fig = pyplot.figure()
    else:
        fig = pyplot.figure(num=num) 

    if size is not None:
        fig.set_figwidth(size[0])
        fig.set_figheight(size[1])

    w = fig.get_figwidth()
    h = fig.get_figheight()

    ax_im = fig.add_subplot(1, 1, 1)

    N   = mat.shape[0]
    idx = numpy.arange(N)  
    if colourbar:
        divider = make_axes_locatable(ax_im)
        ax_cb   = divider.new_vertical(size="10%", pad=0.1, pack_start=True)
        fig.add_axes(ax_cb)


    mat_copy = mat.copy()

    #Null the upper triangle, including the main diagonal.
    idx_null           = numpy.triu_indices(mat_copy.shape[0])
    mat_copy[idx_null] = numpy.nan

    #Min max values
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

    #The call to imshow produces the matrix plot:
    im = ax_im.imshow(mat_copy, origin='upper', interpolation='nearest',
                      vmin=color_min, vmax=color_max, cmap=cmap)

    #Formatting:
    ax = ax_im
    ax.grid(True)
    #Label each of the cells with the row and the column:
    if node_labels is not None:
        for i in xrange(0, mat_copy.shape[0]):
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

    #Make the tick-marks invisible:
    for line in ax.xaxis.get_ticklines():
        line.set_markeredgewidth(0)

    for line in ax.yaxis.get_ticklines():
        line.set_markeredgewidth(0)

    ax.set_axis_off()

    if title is not None:
        ax.set_title(title)

    if colourbar:
        #Set the ticks - if 0 is in the interval of values, set that, as well
        #as the min, max values:
        if min_val < 0:
            ticks = [color_min, min_val, 0, max_val, color_max]
        #set the min, mid and  max values:
        else:
            ticks = [color_min, min_val, (color_max- color_min)/2., max_val, color_max]


        #colourbar:
        cb = fig.colorbar(im, cax=ax_cb, orientation='horizontal',
                          cmap=cmap,
                          norm=im.norm,
                          boundaries=numpy.linspace(color_min, color_max, 256),
                          ticks=ticks,
                          format='%.2f')

    fig.sca(ax)

    return fig


#import pdb; pdb.set_trace()
##----------------------------------------------------------------------------##
##-                   mayavi based plotting functions                        -##
##----------------------------------------------------------------------------##
try:
    from mayavi import mlab

    IMPORTED_MAYAVI = True
except ImportError:
    LOG.error("Mayavi is needed for this demo but due to sizing and packaging constraints we are not distributing it. "
              "If you want to see the actual plot you should use the github version and install all the required "
              "dependencies as described here: (advanced users only)"
              "https://github.com/the-virtual-brain/docs/blob/trunk/InstallationManual/InstallationManual.rst")
    IMPORTED_MAYAVI = False
    #raise

if IMPORTED_MAYAVI:
    @mlab.animate(delay=41, ui=True)
    def surface_timeseries(surface, data, step=1):
        """
        
        """
        fig = mlab.figure(figure="surface_timeseries", fgcolor=(0.5, 0.5, 0.5))
        #Plot an initial surface and colourbar #TODO: Change to use plot_surface function, see below.
        surf_mesh = mlab.triangular_mesh(surface.vertices[:, 0],
                                         surface.vertices[:, 1],
                                         surface.vertices[:, 2],
                                         surface.triangles,
                                         scalars=data[0, :],
                                         vmin=data.min(), vmax=data.max(),
                                         figure=fig)
        mlab.colorbar(object=surf_mesh, orientation="vertical")

        #Handle for the surface object and figure
        surf = surf_mesh.mlab_source

        #Time #TODO: Make actual time rather than points, where/if possible.
        tpts = data.shape[0]
        time_step = mlab.text(0.85, 0.125, ("0 of %s" % str(tpts)),
                              width=0.0625, color=(1, 1, 1), figure=fig,
                              name="counter")

        #Movie
        k = 0
        while 1:
            if abs(k) >= tpts:
                k = 0
            surf.set(scalars=data[k, :])
            time_step.set(text=("%s of %s" % (str(k), str(tpts))))
            k += step
            yield
        mlab.show(stop=True)
        #--------------------------------------------------------------------------#


    #TODO: Make, posssibly with a wrapper function, to work directly with 
    #      SurfacePattern object... Inner function name plot_surface

    def plot_surface(surface, fig=None, name=None, op=1.0, rep='surface'):
        """
        """
        if fig is None:
            fig = mlab.figure(figure=name, fgcolor=(0.5, 0.5, 0.5))

        surf_mesh = mlab.triangular_mesh(surface.vertices[:, 0],
                                         surface.vertices[:, 1],
                                         surface.vertices[:, 2],
                                         surface.triangles,
                                         color=(0.7, 0.67, 0.67),
                                         opacity=op,
                                         representation=rep,
                                         figure=fig)

        return surf_mesh


    def surface_orientation(surface, normals="triangles", name=None):
        """
        """
        fig = mlab.figure(figure=name, fgcolor=(0.5, 0.5, 0.5))
        surf_mesh = mlab.triangular_mesh(surface.vertices[:, 0],
                                         surface.vertices[:, 1],
                                         surface.vertices[:, 2],
                                         surface.triangles,
                                         color=(0.7, 0.67, 0.67),
                                         figure=fig)
        if normals == "triangles":
            surf_orient = mlab.quiver3d(surface.triangle_centres[:, 0],
                                        surface.triangle_centres[:, 1],
                                        surface.triangle_centres[:, 2],
                                        surface.triangle_normals[:, 0],
                                        surface.triangle_normals[:, 1],
                                        surface.triangle_normals[:, 2])
        elif normals == "vertices":
            surf_orient = mlab.quiver3d(surface.vertices[:, 0],
                                        surface.vertices[:, 1],
                                        surface.vertices[:, 2],
                                        surface.vertex_normals[:, 0],
                                        surface.vertex_normals[:, 1],
                                        surface.vertex_normals[:, 2])
        else:
            LOG.error("normals must be either 'triangles' or 'vertices'")

        return (surf_mesh, surf_orient)


    def surface_parcellation(cortex_boundaries, colouring, mapping_colours, colour_rgb, interaction=False):
        """
        """
        number_of_vertices = cortex_boundaries.cortex.vertices.shape[0]
        number_of_triangles = cortex_boundaries.cortex.triangles.shape[0]

        number_of_regions = len(cortex_boundaries.region_neighbours)
        alpha = 255
        lut = numpy.zeros((number_of_regions, 4), dtype=numpy.uint8)
        for k in range(number_of_regions):
            lut[k] = numpy.hstack((colour_rgb[mapping_colours[colouring[k]]], alpha))

        fig = mlab.figure(figure="surface parcellation", bgcolor=(0.0, 0.0, 0.0), fgcolor=(0.5, 0.5, 0.5))
        surf_mesh = mlab.triangular_mesh(cortex_boundaries.cortex.vertices[:number_of_vertices//2, 0],
                                         cortex_boundaries.cortex.vertices[:number_of_vertices//2, 1],
                                         cortex_boundaries.cortex.vertices[:number_of_vertices//2, 2],
                                         cortex_boundaries.cortex.triangles[:number_of_triangles//2, :],
                                         scalars=cortex_boundaries.cortex.region_mapping[:number_of_vertices//2],
                                         figure=fig)
        surf_mesh.module_manager.scalar_lut_manager.lut.number_of_colors = number_of_regions
        surf_mesh.module_manager.scalar_lut_manager.lut.table = lut

        #TODO: can't get region labels to associate with colorbar...
        #mlab.colorbar(object=surf_mesh, orientation="vertical")

        x = cortex_boundaries.boundary[:, 0]
        y = cortex_boundaries.boundary[:, 1]
        z = cortex_boundaries.boundary[:, 2]
        bpts = mlab.points3d(x, y, z, color=(0.25, 0.05, 0.05), scale_factor=1)
        mlab.show(stop=interaction)
        return surf_mesh, bpts


    def surface_pattern(surface, vertex_colours):
        """
        Plot a surface and colour it based on a vector of length number of 
        vertices (vertex_colours).

        * How to obtain a pretty picture (from Mayavi's gui): 
        
          - set surf_mesh color to rgb(237, 217, 221)
          - add a surface module derived from surf_mesh; set 'Actor' 
            representation to wireframe; colour 'gray'.
          - enable contours of scalar_surf  
        """
        #surf_mesh = plot_surface(surface, name="surface pattern")
        fig = mlab.figure(figure="surface pattern", fgcolor=(0.5, 0.5, 0.5))
        surf_mesh = mlab.triangular_mesh(surface.vertices[:, 0],
                                         surface.vertices[:, 1],
                                         surface.vertices[:, 2],
                                         surface.triangles,
                                         figure=fig)
        sm_obj = surf_mesh.mlab_source
        scalar_data = surf_mesh.mlab_source.dataset.point_data
        scalar_data.scalars = vertex_colours
        scalar_data.scalars.name = 'Scalar data'
        scalar_data.update()
        scalar_mesh = mlab.pipeline.set_active_attribute(surf_mesh, point_scalars='Scalar data')
        scalar_surf = mlab.pipeline.surface(scalar_mesh)
        mlab.show(stop=True)
        return sm_obj


    def xmas_balls(connectivity, 
                 labels=True, labels_indices=None, 
                 balls_colormap='Blues', 
                 bgcolor = (0.5, 0.5, 0.5),
                 node_data=None, node_size=4.,
                 edge_data=True, edge_color=(0.8, 0.8, 0.8), edge_size=0.2,
                 text_size=0.042, text_color=(0, 0, 0),
                 remove_nodes=False, nbunch=[], 
                 remove_edges=False, ebunch=[]):
        """
        Plots coloured balls at the region centres of connectivity, colour and
        size is determined by a vector of length number of regions (node_data).
        
        Optional: adds the connections between pair of nodes.
        
        """

        mlab.figure(1, bgcolor=bgcolor)

        # Get graph
        G = nx.from_numpy_matrix(numpy.matrix(connectivity.weights))

        # Get the subgraph of nodes in nbunch
        if remove_nodes:
            G.remove_nodes_from([n for n in G if n not in set(nbunch)])
            #G.remove_nodes_from([node for node,degree in G.degree().items() if degree < 2])

        if remove_edges:
            G.remove_edges_from([e for e in G.edges() if e not in ebunch])


        # scalar colors
        if node_data is not None:
            scalars = node_data
            #mlab.colorbar(orientation="vertical")
        else:
            scalars = numpy.array(G.nodes())*20

        pts = mlab.points3d(connectivity.centres[:,0], 
                            connectivity.centres[:,1], 
                            connectivity.centres[:,2],
                            scalars,
                            #mask_points=1,
                            scale_factor = node_size,
                            scale_mode = 'none',
                            colormap = balls_colormap,
                            resolution = 5,
                            opacity=0.01)

        if labels:
            if labels_indices is not None:
                for i, (idx) in enumerate(labels_indices):
                    x = connectivity.centres[idx, 0]
                    y = connectivity.centres[idx, 1]
                    z = connectivity.centres[idx, 2]
                    label = mlab.text(x, y, connectivity.region_labels[idx], 
                              z=z,
                              width=text_size, 
                              name=str(connectivity.region_labels[idx]), 
                              color=text_color)
                    label.property.shadow = False
            else:
                for i, (x, y, z) in enumerate(connectivity.centres):
                    label = mlab.text(x, y, connectivity.region_labels[i], 
                              z=z,
                              width=text_size, 
                              name=str(connectivity.region_labels[i]), 
                              color=text_color)
                    label.property.shadow = False

        if edge_data:
            pts.mlab_source.dataset.lines = numpy.array(G.edges())
            tube = mlab.pipeline.tube(pts, tube_radius = edge_size)
            mlab.pipeline.surface(tube, color=edge_color, representation='wireframe', opacity=0.3)

        #mlab.show()

            # stop the scene
            #mlab.show(stop=True)


    def connectivity_3d(connectivity, order=None, edge_cutoff=None):
        """
        Plots a 3D representation of the delayed-connectivity structure.
        See Fig. 3 in (Knock et al 2009)

        [Nodes x Nodes x Delays]
        
        Original script can be found at: 
        BrainNetworkModels_3.1/PlottingTools/PlotConnectivity3D.m
        
        """

        fig = mlab.figure(figure="Connectivity 3D", bgcolor=(0.0, 0.0, 0.0))

        N = connectivity.number_of_regions // 2
        minW = connectivity.weights.min()
        maxW = connectivity.weights.max()

        if connectivity.delays is None:
            connectivity.configure()

        minD = connectivity.delays.min()
        maxD = connectivity.delays.max()
        stepD = (maxD - minD) / 10.

        if order is None:
            order = numpy.arange(0, N)

        if edge_cutoff is None:
            edge_cutoff = minW

        # colourmap to emphasise large numbers
        #MAP = numpy.loadtxt('../plot/colourmaps/BlackToBlue')
        #mapstep = 1. / MAP.shape[0]


        # Loop over connectivity matrix, colouring and one cube per matrix element
        K = []
        D = []
        M = []
        S = []
        for k in range(N):
            for m in range(N):
                if connectivity.weights[k, m] != 0:
                    if k != m:
                        #not self connection (diagonal)
                        if connectivity.weights[k, m] > edge_cutoff:
                            K.append(k + 2.)
                            D.append(connectivity.delays[k, m] + stepD)
                            M.append(m + 2.0)
                            S.append(connectivity.weights[k, m])
        mlab.points3d(K, D, M, S, mode='cube')
        mlab.show(stop=True)


        #--------------------------------------------------------------------------#


    ##----------------------------------------------------------------------------##
    ##-                    plotting functions for analysis output                -##
    ##----------------------------------------------------------------------------##

    def plot_matrix(mat, fig_name='plot_this_matrix', connectivity=None):
        """
        An embellished matshow display
        """
        #NOTE: I could add more stuff in plot_connectivity, but I rather have
        # a dummy function for displaying a pretty matrix with the 
        # value of each element.

        fig = pyplot.figure(num=fig_name)
        ax = fig.gca()
        res = ax.imshow(mat, cmap=pyplot.cm.jet, interpolation='nearest', alpha=0.6)

        if connectivity is not None:
            order = numpy.arange(connectivity.number_of_regions)
            labels = connectivity.region_labels
            pyplot.xticks(numpy.arange(connectivity.number_of_regions), list(labels[order]), fontsize=9, rotation=90)
            pyplot.yticks(numpy.arange(connectivity.number_of_regions), list(labels[order]), fontsize=9)

        fig.colorbar(res)
        width = mat.shape[0]
        height = mat.shape[1]

        for x in xrange(width):
            for y in xrange(height):
                ax.annotate(str(int(mat[x][y])),
                            xy=(y, x),
                            horizontalalignment='center',
                            verticalalignment='center',
                            fontsize=7)





if __name__ == '__main__':
    # Do some stuff that tests or makes use of this module... 
    pass


##- EoF -##
