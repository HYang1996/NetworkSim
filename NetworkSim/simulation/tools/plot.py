__author__ = ["Hongyi Yang", "Cheuk Ming Chung"]
__all__ = [
    "init",
    "plot_latency_heatmap",
    "plot_latency_scatter",
    "plot_latency",
    "plot_latency_throughput",
    "plot_latency_3d",
    "plot_count",
    "plot_batch_throughput",
    "plot_analytical_simulation_latency",
    "save_plot",
    "save_all_plots",
    "plot_on_grid",
    "plot_queue_size"
]

import gc
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import rc
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.axes_grid1 import make_axes_locatable
import warnings
import os

from NetworkSim.simulation.tools.performance_analysis import get_transfer_delay

latency_heatmap_size = [5, 5]
latency_scatter_size = [6, 5]
count_size = [5, 5]
latency_throughput_size = [6, 5]
ram_queue_size = [6, 5]


def init():
    """
    Plot environment initialisation.
    """
    gc.collect()
    sns.set_theme(style="ticks")
    sns.set_context("paper")
    rc('font', **{'family': 'sans-serif', 'sans-serif': ['Helvetica']})
    rc('text', usetex=True)
    matplotlib.rcParams['mathtext.fontset'] = 'stix'
    matplotlib.rcParams['font.family'] = 'STIXGeneral'
    SMALL_SIZE = 7
    MEDIUM_SIZE = 9
    LARGE_SIZE = 11
    BIGGER_SIZE = 13
    rc('font', size=SMALL_SIZE)          # controls default text sizes
    rc('axes', titlesize=LARGE_SIZE)     # fontsize of the axes title
    rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
    rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize
    rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
    sns.set_palette('RdBu_r')
    warnings.filterwarnings("ignore")


def plot_latency_heatmap(latency, type=None, fig=None, ax=None, title=None):
    """Plot average latency of all nodes in a simulator as a heatmap.

    Parameters
    ----------
    latency : pandas DataFrame
        A DataFrame containing the latency information, generated from ``summary``.
    type : string, optional
        Type of latency to be plotted, by default ``None``.
    fig : figure, optional
        Figure to be plotted on, by default ``None``.
    ax : axis, optional
        Axis to be plotted on, by default ``None``.
    title : string, optional
        Plot title, by default ``None``.

    Returns
    -------
    fig : figure
        Plot figure object.
    """
    init()
    _queueing_delay_keywords = {'queueing delay', 'qd'}
    if type in _queueing_delay_keywords:
        label = 'Average Queueing Delay (ns)'
    else:
        label = 'Average Transfer Delay (ns)'
    start, end = min(latency.columns), max(latency.columns)
    width, height = latency_heatmap_size[0], latency_heatmap_size[1]
    if fig is None and ax is None:
        fig, ax1 = plt.subplots(1, 1, figsize=(width, height), dpi=300)
    else:
        fig = fig
        ax1 = ax
    divider = make_axes_locatable(ax1)
    cax1 = divider.append_axes('right', size='5%', pad=0.2)
    sns.heatmap(data=latency, cmap='RdBu_r', ax=ax1, lw=.25,
                xticklabels=10, yticklabels=10, square=True, cbar_ax=cax1,
                cbar_kws={'label': label, 'shrink': .6, 'pad': .1},
                )
    ax1.tick_params(width=0.5)
    ax1.set_xlim([start, end])
    ax1.set_ylim([end, start])
    ax1.xaxis.set_tick_params(width=0.5)
    ax1.yaxis.set_tick_params(width=0.5)
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=0)
    ax1.set_yticklabels(ax1.get_yticklabels(), rotation=0)
    ax1.set_xlabel('Destination Node')
    ax1.set_ylabel('Source Node')
    frame_linewidth = 1
    ax1.axhline(y=start, color='k', linewidth=frame_linewidth)
    ax1.axhline(y=end, color='k', linewidth=frame_linewidth)
    ax1.axvline(x=start, color='k', linewidth=frame_linewidth)
    ax1.axvline(x=end, color='k', linewidth=frame_linewidth)
    if title is not None:
        ax1.set_title(title)
    fig.tight_layout()
    return fig


def plot_latency_scatter(latency, node_id):
    """
    Scatter plot of latency information of one node, \
        both as a source node and as a destination node.

    Parameters
    ----------
    latency : list
        The list of latency from ``BaseSimulator``.
    node_id : int
        The ID of the node of interest.
    """
    init()
    latency_as_source = []
    latency_as_destination = []
    source_ids = []
    destination_ids = []
    for latency in latency:
        if latency['Source ID'] == node_id:
            destination_ids.append(latency['Destination ID'])
            latency_as_source.append(latency['Transfer Delay'])
        if latency['Destination ID'] == node_id:
            source_ids.append(latency['Source ID'])
            latency_as_destination.append(latency['Transfer Delay'])
    x = [destination_ids, source_ids]
    y = [latency_as_source, latency_as_destination]
    titles = ['Latency as Source Node', 'Latency as Destination Node']
    xlabels = ['Destination Node', 'Source Node']
    ylabel = 'Transfer Latency (ns)'
    width, height = latency_scatter_size[0], latency_scatter_size[1]
    fig, axes = plt.subplots(2, 1, figsize=(width, height), dpi=300)
    for i in range(2):
        sns.scatterplot(x=x[i], y=y[i], ax=axes[i], s=25, alpha=.5, lw=1,
                        edgecolors='white', color=sns.color_palette('RdBu_r')[0])
        axes[i].set_ylabel(ylabel)
        axes[i].set_xlabel(xlabels[i])
        axes[i].yaxis.grid(True)
        axes[i].set_title(titles[i], fontsize=13)
    fig.tight_layout()
    return fig


def plot_count(packet_count, fig=None, ax=None, title=None):
    """
    Plot transmission packet count as a heatmap.

    Parameters
    ----------
    packet_count : pandas DataFrame
        A DataFrame containing the packet count summary.
    fig : figure, optional
        Figure to be plotted on, by default ``None``.
    ax : axis, optional
        Axis to be plotted on, by default ``None``.
    title : string, optional
        Plot title, by default ``None``.
    """
    init()
    width, height = count_size[0], count_size[1]
    if fig is None and ax is None:
        fig, ax1 = plt.subplots(1, 1, figsize=(width, height), dpi=300)
    else:
        fig = fig
        ax1 = ax
    start, end = min(packet_count.columns), max(packet_count.columns)
    divider = make_axes_locatable(ax1)
    cax1 = divider.append_axes('right', size='5%', pad=0.2)
    sns.heatmap(data=packet_count, cmap='RdBu_r', ax=ax1, lw=.25, cbar_ax=cax1,
                cbar_kws={'label': 'Number of Packets Transmitted', 'shrink': .6, 'pad': 0.1},
                xticklabels=10, yticklabels=10, square=True)
    ax1.tick_params(width=0.5)
    ax1.set_xlim([start, end])
    ax1.set_ylim([end, start])
    ax1.xaxis.set_tick_params(width=0.5)
    ax1.yaxis.set_tick_params(width=0.5)
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=0)
    ax1.set_yticklabels(ax1.get_yticklabels(), rotation=0)
    ax1.set_xlabel('Destination Node')
    ax1.set_ylabel('Source Node')
    frame_linewidth = 1
    ax1.axhline(y=start, color='k', linewidth=frame_linewidth)
    ax1.axhline(y=end, color='k', linewidth=frame_linewidth)
    ax1.axvline(x=start, color='k', linewidth=frame_linewidth)
    ax1.axvline(x=end, color='k', linewidth=frame_linewidth)
    if title is not None:
        ax1.set_title(title)
    fig.tight_layout()
    return fig


def plot_latency_throughput(latency):
    """Plot latency and throughput of a simulation across time.

    Parameters
    ----------
    latency : list
        The list of `latency` attribute information from ``BaseSimulator``.
    """
    init()
    time = list(item['Latency Timestamp'] for item in latency)
    delay = list(item['Transfer Delay'] for item in latency)
    rate = list(item['Data Rate'] for item in latency)
    y = [delay, rate]
    xlabel = 'Time (ns)'
    ylabels = ['Transfer Delay (ns)', 'Throughput (Gbit/s)']
    titles = ['Overall Transfer Delay', 'Overall Throughput']
    width, height = latency_throughput_size[0], latency_throughput_size[1]
    fig, axes = plt.subplots(2, 1, figsize=(width, height), dpi=300)
    for i in range(2):
        sns.lineplot(x=time, y=y[i], markers=True,
                     dashes=False, ax=axes[i], lw=1,
                     color=sns.color_palette('RdBu_r')[0])
        axes[i].set_ylabel(ylabels[i])
        axes[i].set_xlabel(xlabel)
        axes[i].xaxis.grid(True)
        axes[i].yaxis.grid(True)
        axes[i].set_title(titles[i], fontsize=13)
    fig.tight_layout()
    return fig


def plot_latency_3d(latency, type):
    """
    3d bar plot of parameters as source/destination pair.

    Parameters
    ----------
    latency : pandas DataFrame
        A DataFrame containing the latency information, generated from ``summary``.
    type : string
        Type of latency to be plotted.
    """
    init()
    _n = len(latency.columns)
    x = y = [i for i in range(_n)]
    T, A = np.meshgrid(x, y)
    _queueing_delay_keywords = {'queueing delay', 'qd'}
    if type in _queueing_delay_keywords:
        zlabel = 'Average Queueing Delay (ns)'
    else:
        zlabel = 'Average Transfer Delay (ns)'
    xlabel = 'Source Node'
    ylabel = 'Destination Node'
    std_plot = False
    if isinstance(latency, tuple):
        mean_df = latency[0]
        std_df = latency[1]
        std_plot = True
    elif isinstance(latency, pd.DataFrame):
        mean_df = latency
    mean = mean_df.values
    if std_plot is True:
        std = std_df.values
        zlabel = ('STD of ' + zlabel)
        std_transpose = std.transpose()
        dz = std_transpose.flatten()
    else:
        mean_transpose = mean.transpose()
        dz = mean_transpose.flatten()
    # Plotting
    fig = plt.figure(figsize=(15, 15), dpi=300)
    ax = fig.gca(projection='3d')

    Xi = T.flatten()
    Yi = A.flatten()
    Zi = np.zeros(mean.size)
    dx = dy = 0.5
    ax.bar3d(Xi, Yi, Zi, dx, dy, dz, color=sns.color_palette('RdBu_r')[0], shade=False)
    ax.view_init(20, 37)
    ax.set_xlabel(xlabel, fontsize=15)
    ax.set_ylabel(ylabel, fontsize=15)
    ax.set_zlabel(zlabel, fontsize=15)
    return fig


def plot_batch_throughput(simulator, show_ci=True):
    """Plot batch throughput of simulations. Confidence intervals demarcated by the SEM values \
        are shown by default. Where the maximum SEM value plotted is 1.

    Parameters
    ----------
    simulator : BaseSimulator
        The simulator used.
    show_ci : bool, optional
        If confidence interval is displayed, by default ``True``.
    """
    # Check for convergence mode
    if not simulator.convergence:
        raise NotImplementedError("This plot function is implemented only "
                                  "for simulators with convergence mode enabled.")
    init()
    stats = simulator.batch_stats
    time = list(item['timestamp'] for item in stats)
    mean = list(item['mean'] for item in stats)
    sem = list(item['sem'] for item in stats)
    upper_ci = []
    lower_ci = []
    xlabel = 'Time (ns)'
    ylabel = 'Throughput (Gbit/s)'
    title = 'Batch Mean Throughput'
    if show_ci:
        for i in range(len(time)):
            if sem[i] > 1:
                sem[i] = 1
            upper_ci.append(mean[i] * (1 + sem[i]))
            lower_ci.append(mean[i] * (1 - sem[i]))
    fig, ax = plt.subplots(1, 1, figsize=(6, 3), dpi=300)
    sns.lineplot(x=time, y=mean, ax=ax, lw=1, color=sns.color_palette('RdBu_r')[0])
    if show_ci:
        ax.fill_between(time, lower_ci, upper_ci, fc=sns.color_palette('RdBu_r')[2], ec=None, alpha=.75)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.xaxis.grid(True)
    ax.yaxis.grid(True)
    ax.set_title(title, fontsize=13)
    fig.tight_layout()
    return fig


def plot_latency(simulator, latency, node_id=None, latency_type=None, bar3d=False, fig=None, ax=None, title=None):
    """
    Function to plot latency information.

    Parameters
    ----------
    simulator : BaseSimulator
        The simulator of choice.
    latency : pandas DataFrame
        The latency summary generated.
    node_id : int, optional
        The node of interest, by default ``None``.
    latnecy_type : string, optional
        The latency type of interset, by default is ``None``, which is transfer delay.
    bar3d : bool, optional
        Enable 3d bar plot for queueing delay, default is ``False``.
    fig : figure, optional
        Figure to be plotted on, by default ``None``.
    ax : axis, optional
        Axis to be plotted on, by default ``None``.
    title : string, optional
        Plot title, by default ``None``.
    """
    if node_id is None:
        if bar3d is False:
            return plot_latency_heatmap(latency, type=latency_type, fig=fig, ax=ax, title=title)
        else:
            return plot_latency_3d(latency, type=latency_type)
    else:
        return plot_latency_scatter(simulator.latency, node_id)


def check_grid_plot_input(simulator, grid):
    """Function to check the inputs of a grid plot.

    Parameters
    ----------
    simulator : ParallelSimulator
        The parallel simulator used.
    grid : list
        The grid to be plotted on.

    Returns
    -------
    row, col : int
        The number of rows and columns in the grid.
    """
    # Check simulator
    from NetworkSim.simulation.simulator.parallel import ParallelSimulator  # Soft dependency
    if not isinstance(simulator, ParallelSimulator):
        raise ValueError("This plot function is only implemented for ParallelSimulator.")
    # Check grid
    if not isinstance(grid, list) or len(grid) != 2:
        raise ValueError("Grid must be a list with length 2 indicating number of rows and columns.")
    # Check row and column dimensions
    if grid[0] < 2 or grid[1] < 2:
        raise ValueError("Both number of rows and number of columns must be larger than 1.")
    return grid[0], grid[1]


def plot_on_grid(simulator, grid, titles, summary_type, latency_type=None):
    """Function to generates plots on a grid.

    Parameters
    ----------
    simulator : ParallelSimulator
        The parallel simulator used.
    grid : list
        The grid used for plotting.
    titles : list
        The list of titles for the subplots.
    summary_type : string
        The summary type corresponding to the plots to be generated, same as that used in `BaseSimulator.summary`.
    latency_type : string, optional
        The type of latency to be plotted, by default ``None``.

    Returns
    -------
    fig : figure
        The figure object produced.
    """
    _row, _col = check_grid_plot_input(simulator=simulator, grid=grid)
    _latency_keywords = {'latency', 'l'}
    _count_keywords = {'count', 'c'}
    # Plot
    init()
    _plot_count = 0
    if summary_type in _latency_keywords:
        _width, _height = latency_heatmap_size[0], latency_heatmap_size[1]
    elif summary_type in _count_keywords:
        _width, _height = count_size[0], count_size[1]
    fig, axes = plt.subplots(_row, _col, figsize=(_width * _row, _height * _col), dpi=300)
    for i in range(_row):
        for j in range(_col):
            if _plot_count > len(simulator.simulator):
                continue
            _simulator = simulator.simulator[_plot_count]
            _summary = _simulator.summary(summary_type=summary_type, latency_type=latency_type)
            if summary_type in _latency_keywords:
                plot_latency(simulator=_simulator, latency=_summary, latency_type=latency_type,
                             fig=fig, ax=axes[i][j], title=titles[_plot_count])
            elif summary_type in _count_keywords:
                plot_count(packet_count=_summary, fig=fig, ax=axes[i][j], title=titles[_plot_count])
            _plot_count += 1
    for i in range(max(_row, _col)):
        fig.tight_layout()
    return fig


def plot_analytical_simulation_latency(simulator, data='auto', show_analytical=True):
    """Plot analytical and simulation transfer delay.

    Parameters
    ----------
    simulator : ParallelSimulator
        The simulator used for the plot.
    data : str, optional
        Range of data used for the plot, chosen from the list:

        - `batch` : Use the data from the last batch when convergence mode is enabled.
        - `extended` : Use the data from the extended run when convergence mode is enabled.
        - `all` : Use all simulation data.
        - `auto` : Automatically determine the range of the data used. `batch` is selected when \
            convergence mode is enabled and `all` is selected when convergence mode is disabled.

        Default is ``auto``.
    show_analytical : bool, optional
        If analytical results are shown on the plot, by default ``True``.
    """
    # Check for data range
    if data not in ['auto', 'batch', 'all']:
        raise ValueError("Plot data range is not recognised.")
    # Compute plot data
    load = []
    analytical_delay = []
    simulation_delay = []
    xlabel = 'Network Source Traffic Load (Gbit/s)'
    ylabel = 'Mean Transfer Delay (ns)'
    for simulator in simulator.simulator:
        load.append(simulator.model.network.num_nodes * simulator.model.constants['average_bit_rate'])
        analytical_delay.append(get_transfer_delay(simulator))
        if data == 'auto':
            if simulator.convergence:
                data_range = 'all'
            else:
                data_range = 'extended'
        else:
            data_range = data
        # TODO: change direct delay calculations to get_delay functions in performance_analysis
        if data_range == 'all':
            latency = simulator.latency
        elif data_range == 'extended':
            start = simulator.batch_stats[-1]['end_index']
            latency = simulator.latency[start:]
        elif data_range == 'batch':
            start = simulator.batch_stats[-1]['start_index']
            latency = simulator.latency[start:]
        delay = np.mean(list(item['Transfer Delay'] for item in latency))
        simulation_delay.append(delay)
    # Plot analytical and simulation result
    if np.isinf(max(analytical_delay)):
        ylim = 1.2 * max(simulation_delay)
    else:
        ylim = 1.2 * max(analytical_delay + simulation_delay)
    init()
    fig, ax = plt.subplots(1, 1, figsize=(5, 3), dpi=300)
    if show_analytical:
        sns.lineplot(x=load, y=analytical_delay, lw=0.75, ls='--', marker='x', markersize=4,
                     markerfacecolor='None', markeredgecolor='k', ax=ax, label='Analytical',
                     color=sns.color_palette('RdBu_r')[-1])
    sns.lineplot(x=load, y=simulation_delay, lw=0.75, ls='-', marker='s', markersize=4,
                 markerfacecolor='None', markeredgecolor='k', ax=ax, label='Simulation',
                 color=sns.color_palette('RdBu_r')[0], ci=95)
    ax.legend(loc='upper left')
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.xaxis.grid(True)
    ax.yaxis.grid(True)
    ax.set_ylim([0, ylim])
    fig.tight_layout()
    return fig


def plot_queue_size(simulator):
    """Plot queue size information for ParallelSimulator.

    Parameters
    ----------
    simulator : ParallelSimulator
        The simulator used for the plot.
    """
    # Check simulator type
    from NetworkSim.simulation.simulator.parallel import ParallelSimulator
    if not isinstance(simulator, ParallelSimulator):
        raise NotImplementedError("This plot is only implemented for ParallelSimulator.")
    # Get queue size information
    mean_size = []
    max_size = []
    load = []
    for individual_simulator in simulator.simulator:
        mean_queue_size, max_queue_size, _ = individual_simulator.summary(summary_type='q')
        mean_size.append(mean_queue_size)
        max_size.append(max_queue_size)
        load.append(individual_simulator.model.constants['average_bit_rate']
                    * individual_simulator.model.network.num_nodes)
    init()
    y = [mean_size, max_size]
    xlabel = 'Overall Network Load (Gbit/s)'
    ylabel = 'Queue Size'
    titles = ['Mean Queue Size in RAM', 'Maximum Queue Size in RAM']
    width, height = ram_queue_size[0], ram_queue_size[1]
    fig, axes = plt.subplots(2, 1, figsize=(width, height), dpi=300)
    for i in range(2):
        sns.lineplot(x=load, y=y[i], markers=True, ci=95,
                     dashes=False, ax=axes[i], lw=1,
                     color=sns.color_palette('RdBu_r')[0])
        axes[i].set_ylabel(ylabel)
        axes[i].set_xlabel(xlabel)
        axes[i].xaxis.grid(True)
        axes[i].yaxis.grid(True)
        axes[i].set_title(titles[i], fontsize=13)
    fig.tight_layout()
    return fig


def save_plot(fig, fname, dir_name=None):
    """Function to save a figure generated in png format.

    Parameters
    ----------
    fig : figure
        The matplotlib figure object to be saved.
    fname : string
        The output file name of the figure.
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))
    if dir_name is None:
        dir_name = 'plots'
    else:
        dir_name = os.path.join('plots', dir_name)
    fpath = os.path.join(dir_path, '../../../', dir_name)
    if not os.path.exists(fpath):
        os.mkdir(fpath)
    fig_name = fpath + "/" + fname
    fig.savefig(fname=fig_name)


def _save_all_basesimulator_plots(simulator, dir_name):
    """Function to save all BaseSimulator plots.

    Parameters
    ----------
    simulator : BaseSimulator
        The simulator whose plots are generated.
    dir_name : string
        Folder name for the plot output files.
    """
    plt.ioff()
    # Overall latency and throughput
    _fig = simulator.summary(format='plot')
    plt.close(_fig)
    save_plot(fig=_fig, fname='latency_throughput', dir_name=dir_name)
    # Transfer and queueing delay
    _fig = simulator.summary(format='plot', summary_type='l')
    plt.close(_fig)
    save_plot(fig=_fig, fname='transfer_delay', dir_name=dir_name)
    _fig = simulator.summary(format='plot', summary_type='l', latency_type='qd')
    plt.close(_fig)
    save_plot(fig=_fig, fname='queueing_delay', dir_name=dir_name)
    # Packet count
    _fig = simulator.summary(format='plot', summary_type='c')
    plt.close(_fig)
    save_plot(fig=_fig, fname='packet_count', dir_name=dir_name)
    # Batch throughput
    _fig = plot_batch_throughput(simulator=simulator)
    plt.close(_fig)
    save_plot(fig=_fig, fname='batch_throughput', dir_name=dir_name)
    del _fig


def _save_all_parallelsimulator_plots(simulator, dir_name, grid, titles):
    plt.ioff()
    # Transfer delay
    _fig = plot_on_grid(simulator=simulator, grid=grid, titles=titles, summary_type='l')
    plt.close(_fig)
    save_plot(fig=_fig, fname='transfer_delay', dir_name=dir_name)
    # Queueing delay
    _fig = plot_on_grid(simulator=simulator, grid=grid, titles=titles, summary_type='l', latency_type='qd')
    plt.close(_fig)
    save_plot(fig=_fig, fname='queueing_delay', dir_name=dir_name)
    # Packet count
    _fig = plot_on_grid(simulator=simulator, grid=grid, titles=titles, summary_type='c')
    plt.close(_fig)
    save_plot(fig=_fig, fname='packet_count', dir_name=dir_name)
    # Analytical and simulation latency
    _fig = plot_analytical_simulation_latency(simulator=simulator)
    plt.close(_fig)
    save_plot(fig=_fig, fname='analytical_simulation_latency', dir_name=dir_name)
    del _fig


def save_all_plots(simulator, dir_name, grid=None, titles=None):
    """Function to automatically generate and save plots of a simulator.

    Parameters
    ----------
    simulator : BaseSimulator or ParallelSimulator
        The simulator whose plots are generated and saved.
    dir_name: string
        The folder name under the `plot` directory to store the simulator's plot images.
    grid : list, optional
        The grid used for plotting, by default ``None``.
    titles : list
        The list of titles for the subplots, by default ``None``.
    """
    # Soft dependencies
    from NetworkSim.simulation.simulator.base import BaseSimulator
    from NetworkSim.simulation.simulator.parallel import ParallelSimulator
    if isinstance(simulator, BaseSimulator):
        return _save_all_basesimulator_plots(simulator=simulator, dir_name=dir_name)
    elif isinstance(simulator, ParallelSimulator):
        return _save_all_parallelsimulator_plots(simulator=simulator, dir_name=dir_name, grid=grid, titles=titles)
    else:
        raise ValueError("A BaseSimulator or ParallelSimulator object is expected.")
