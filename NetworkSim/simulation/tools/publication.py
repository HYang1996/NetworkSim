__author__ = ['Hongyi Yang']
__all__ = [
    'init',
    'plot_delay',
    'plot_buffer',
    'plot_throughput',
    'plot_delay_heatmap',
    'plot_packet_heatmap',
    'plot_ook_ber',
    'plot_scaled_network_delay',
    '_compute_scaled_network_transfer_delay',
]

import gc
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import rc
from mpl_toolkits.axes_grid1 import make_axes_locatable
import warnings
import numpy as np
from scipy.special import erfc
from scipy.stats import ncx2

from NetworkSim.architecture.base.network import Network
from NetworkSim.architecture.setup.model import Model
from NetworkSim.simulation.simulator.base import BaseSimulator
from NetworkSim.simulation.simulator.parallel import ParallelSimulator
from NetworkSim.simulation.tools.performance_analysis import \
    get_transfer_delay, get_queueing_delay, get_min_transfer_delay, get_service_delay, \
    get_final_batch_delay, get_extended_run_delay, get_overall_delay, \
    get_final_batch_throughput, get_extended_run_throughput, get_overall_throughput

queueing_delay_keywords = {'queueing delay', 'qd', 'queueing'}
transfer_delay_keywords = {'transfer delay', 'td', 'transfer'}

overall_range_keywords = {'overall', 'all'}
extended_range_keywords = {'extended', 'e'}
final_batch_range_keywords = {'final batch', 'fb'}

load_keywards = {'load', 'l'}
scale_keywords = {'scale', 's'}

mean_keywords = {'mean', 'Mean', 'MEAN'}
min_keywords = {'min', 'Min', 'MIN'}
max_keywords = {'max', 'Max', 'MAX'}
t_min_keywords = {'tmin', 'TMIN'}

colors = [
    sns.color_palette('RdBu_r')[0],
    sns.color_palette('PRGn_r')[0],
    sns.color_palette('PRGn_r')[-1],
    sns.color_palette('Paired')[7],
    sns.color_palette('RdBu_r')[-1],
]

markers = [
    's',
    '^',
    'o',
    'D'
]

FIG_WIDTH = 3
FIG_HEIGHT = 3
MARKERSIZE = 2.5
MARKER_EDGE_WIDTH = .4
DPI = 600
CAX_FONT_SIZE = 6


def _check_for_ParallelSimulator(simulator):
    if not isinstance(simulator, ParallelSimulator):
        raise ValueError("ParallelSimulator is expected.")


def _check_for_BaseSimulator(simulator):
    if not isinstance(simulator, BaseSimulator):
        raise ValueError("BaseSimulator is expected.")


def _check_delay_keywords(delay):
    if delay not in queueing_delay_keywords and delay not in transfer_delay_keywords:
        raise ValueError("Delay type is not recognised.")


def _check_span_keywords(span):
    if span not in overall_range_keywords and span not in extended_range_keywords \
            and span not in final_batch_range_keywords:
        raise ValueError("Time span is not recognised.")


def _check_metric_keywords(metric):
    if metric not in mean_keywords and metric not in min_keywords \
            and metric not in max_keywords and metric not in t_min_keywords:
        raise ValueError("Metric is not recognised.")


def _check_scaled_network_keywords(data_type):
    if data_type not in load_keywards and data_type not in scale_keywords:
        raise ValueError("Scaled network plot data type is not recognised.")


def _convert_keywords(keyword):
    if keyword in queueing_delay_keywords:
        return "Queueing Delay"
    elif keyword in transfer_delay_keywords:
        return "Transfer Delay"
    elif keyword in mean_keywords:
        return "Average"
    elif keyword in min_keywords:
        return "Minimum"
    elif keyword in max_keywords:
        return "Maximum"
    elif keyword in t_min_keywords:
        return "Theoretical Minimum"


def _get_delay(simulator, delay, span, metric, analytical):
    _check_for_BaseSimulator(simulator)
    _check_delay_keywords(delay=delay)
    _check_span_keywords(span=span)
    _check_metric_keywords(metric=metric)
    if span in overall_range_keywords:
        results = get_overall_delay(simulator=simulator)
    elif span in extended_range_keywords:
        results = get_extended_run_delay(simulator=simulator)
    elif span in final_batch_range_keywords:
        results = get_final_batch_delay(simulator=simulator)
    analytical_delay = -1
    if delay in queueing_delay_keywords:
        if metric in min_keywords:
            simulation_delay = results['min_queueing_delay']
        elif metric in max_keywords:
            simulation_delay = results['max_queueing_delay']
        elif metric in mean_keywords:
            simulation_delay = results['mean_queueing_delay']
        if analytical:
            analytical_delay = get_queueing_delay(simulator=simulator) + get_service_delay(simulator=simulator)
    elif delay in transfer_delay_keywords:
        if metric in min_keywords:
            simulation_delay = results['min_transfer_delay']
        elif metric in max_keywords:
            simulation_delay = results['max_transfer_delay']
        elif metric in mean_keywords:
            simulation_delay = results['mean_transfer_delay']
        elif metric in t_min_keywords:
            simulation_delay = get_min_transfer_delay(simulator=simulator)
        if analytical:
            analytical_delay = get_transfer_delay(simulator=simulator)
    return analytical_delay, simulation_delay


def _get_throughput(simulator, span):
    _check_for_BaseSimulator(simulator=simulator)
    _check_span_keywords(span=span)
    if span in overall_range_keywords:
        mean_throughput = get_overall_throughput(simulator=simulator)
    elif span in extended_range_keywords:
        mean_throughput = get_extended_run_throughput(simulator=simulator)
    elif span in final_batch_range_keywords:
        mean_throughput = get_final_batch_throughput(simulator=simulator)
    return mean_throughput


def _get_buffer_size(simulator, metric):
    _check_for_BaseSimulator(simulator)
    _check_metric_keywords(metric=metric)
    mean_queue_size, max_queue_size, _ = simulator.summary(summary_type='q')
    # Compute buffer size in kB
    if metric in mean_keywords:
        buffer_queue = mean_queue_size
    elif metric in max_keywords:
        buffer_queue = max_queue_size
    else:
        buffer_queue = 0
    buffer_size = buffer_queue * 1500 / 1000
    return buffer_queue, buffer_size


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
    SMALLER_SIZE = 6
    SMALL_SIZE = 7
    MEDIUM_SIZE = 8
    LARGE_SIZE = 9
    BIGGER_SIZE = 10
    rc('font', size=SMALL_SIZE)          # controls default text sizes
    rc('axes', titlesize=LARGE_SIZE)     # fontsize of the axes title
    rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
    rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    rc('legend', fontsize=SMALLER_SIZE)  # legend fontsize
    rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
    sns.set_palette('RdBu_r')
    warnings.filterwarnings("ignore")


def plot_delay(simulator, delay='td', span='e', metrics=['mean'], analytical=True, semilog=True):
    """Plot delay statistics of a ParallelSimulator.

    Parameters
    ----------
    simulator : ParallelSimulator
        The simulator used.
    delay : str, optional
        The type of delay to be plotted, by default ``td``, chosen from the following:

        - `qd`, `queueing delay` or `queueing`
            The overall queueing delay.
        - `td`, `transfer delay` or `transfer`
            The transfer delay.
    span : str, optional
        The time span of the delay statistics in the simulation, by default ``extended``, chosen from the following:

        - `overall` or `all`
            The entire duration of the simulation.
        - `final batch` or `fb`
            The statistics from the final batch when simulation converges.
        - `extended` or `e`
            The extended period of the simulation.
    metrics : list, optional
        A list of the metric(s) of delay statistics, by default ``mean``, chosen from the following:

        - `mean`
            Mean delay statistics.
        - `min`
            Minimum delay statistics.
        - `max`
            Maximum delay statistics.
    analytical : bool, optional
        If analytical results are plotted, by default True
    semilog : bool, optional
        If to plot data on a semi-logarithmic scale

    Returns
    -------
    fig : Figure
        The figure plotted.
    """
    _check_for_ParallelSimulator(simulator)
    # Get plot data
    analytical_delays = []
    simulation_delays = []
    load = []
    for metric in metrics:
        _analytical_delays = []
        _simulation_delays = []
        _load = []
        for individual_simulator in simulator.simulator:
            analytical_delay, simulation_delay = _get_delay(
                simulator=individual_simulator,
                delay=delay,
                span=span,
                metric=metric,
                analytical=analytical
            )
            _analytical_delays.append(analytical_delay / 1000)
            _simulation_delays.append(simulation_delay / 1000)
            _load_percentage = individual_simulator.model.constants['average_bit_rate'] / \
                individual_simulator.model.constants['maximum_bit_rate'] * 100
            if individual_simulator.bidirectional:
                _load.append(_load_percentage / 2)
            else:
                _load.append(_load_percentage)
        if not analytical_delays:
            analytical_delays = _analytical_delays
        simulation_delays.append(_simulation_delays)
        load.append(_load)
    # Generate plot
    init()
    fig, ax = plt.subplots(1, 1, figsize=(FIG_WIDTH * 1.05, FIG_HEIGHT), dpi=DPI)
    xlabel = "Network Traffic Load ($\%$)"
    ylabel = _convert_keywords(delay) + " ($\mu$s)"
    if analytical:
        sns.lineplot(x=load[0], y=analytical_delays, lw=0.75, ls='--', marker='x', markersize=MARKERSIZE,
                     markerfacecolor='None', markeredgecolor='k', markeredgewidth=MARKER_EDGE_WIDTH, ax=ax,
                     color=sns.color_palette('RdBu_r')[-1], ci=None, label='Analytical Average')
    for i in range(len(metrics)):
        if analytical:
            label = "Simulation "
        else:
            label = ""
        label += _convert_keywords(metrics[i])
        sns.lineplot(x=load[i], y=simulation_delays[i], lw=0.75, ls='-', marker=markers[i], markersize=MARKERSIZE,
                     markerfacecolor='None', markeredgecolor='k', markeredgewidth=MARKER_EDGE_WIDTH, ax=ax,
                     color=colors[i], ci=95, label=label)
    if analytical or len(metrics) > 1:
        ax.legend()
    else:
        ax.legend().set_visible(False)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.grid(which='both')
    if semilog:
        ax.set_yscale('log')
        ax.minorticks_on()
    else:
        ax.get_xaxis().set_minor_locator(matplotlib.ticker.AutoMinorLocator())
        ax.get_yaxis().set_minor_locator(matplotlib.ticker.AutoMinorLocator())
    ax.xaxis.grid(True, lw=.5, which='major')
    ax.yaxis.grid(True, lw=.5, which='major')
    ax.xaxis.grid(True, lw=.3, which='minor', ls=':')
    ax.yaxis.grid(True, lw=.3, which='minor', ls=':')
    ax.tick_params(width=.5, which='major')
    ax.tick_params(width=.3, which='minor')
    for axis in ['top', 'bottom', 'left', 'right']:
        ax.spines[axis].set_linewidth(0.5)
    ax.set_aspect(1 / ax.get_data_ratio(), adjustable='box')
    fig.tight_layout()
    return fig


def plot_throughput(simulator, span='e', semilog=False):
    """Plot mean throughput statistics of a ParallelSimulator.

    Parameters
    ----------
    simulator : ParallelSimulator
        The simulator used.
    span : str, optional
        The time span of the delay statistics in the simulation, by default ``extended``, chosen from the following:

        - `overall` or `all`
            The entire duration of the simulation.
        - `final batch` or `fb`
            The statistics from the final batch when simulation converges.
        - `extended` or `e`
            The extended period of the simulation.
    semilog : bool, optional
        If to plot data on a semi-logarithmic scale, by default ``False``.

    Returns
    -------
    fig : Figure
        The figure plotted.
    """
    _check_for_ParallelSimulator(simulator)
    # Get plot data
    throughput = []
    load = []
    for individual_simulator in simulator.simulator:
        mean_throughput = _get_throughput(simulator=individual_simulator, span=span)
        throughput.append(mean_throughput / 1000)
        load.append(individual_simulator.model.network.num_nodes *
                    individual_simulator.model.constants['average_bit_rate'] / 1000)
    # Generate plot
    init()
    fig, ax = plt.subplots(1, 1, figsize=(FIG_WIDTH, FIG_HEIGHT), dpi=DPI)
    xlabel = "Network Traffic Load (Tbit/s)"
    ylabel = "Average Throughput (Tbit/s)"
    sns.lineplot(x=load, y=throughput, lw=0.75, ls='-', marker='s', markersize=MARKERSIZE,
                 markerfacecolor='None', markeredgecolor='k', markeredgewidth=MARKER_EDGE_WIDTH, ax=ax,
                 color=sns.color_palette('RdBu_r')[0], ci=95)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.grid(which='both')
    if semilog:
        ax.set_yscale('log')
        ax.minorticks_on()
        ax.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
        ax.ticklabel_format(axis='y', style='plain')
    else:
        ax.get_xaxis().set_minor_locator(matplotlib.ticker.AutoMinorLocator())
        ax.get_yaxis().set_minor_locator(matplotlib.ticker.AutoMinorLocator())
    ax.xaxis.grid(True, lw=.5, which='major')
    ax.yaxis.grid(True, lw=.5, which='major')
    ax.xaxis.grid(True, lw=.3, which='minor', ls=':')
    ax.yaxis.grid(True, lw=.3, which='minor', ls=':')
    ax.tick_params(width=.5, which='major')
    ax.tick_params(width=.3, which='minor')
    for axis in ['top', 'bottom', 'left', 'right']:
        ax.spines[axis].set_linewidth(0.5)
    ax.set_aspect(1 / ax.get_data_ratio(), adjustable='box')
    fig.tight_layout()
    return fig


def plot_buffer(simulator, metrics=['mean', 'max'], semilog=True):
    """Plot buffer size statistics of a ParallelSimulator.

    Parameters
    ----------
    simulator : ParallelSimulator
        The simulator used.
    metric : list, optional
        A list of the metric(s) of delay statistics, by default ``['mean', 'max']``, \
            chosen from the following:

        - `mean`
            Mean delay statistics.
        - `min`
            Minimum delay statistics.
        - `max`
            Maximum delay statistics.
    semilog : bool, optional
        If to plot data on a semi-logarithmic scale, by default ``True``.

    Returns
    -------
    fig : Figure
        The figure plotted.
    """
    _check_for_ParallelSimulator(simulator)
    # Get plot data
    buffer = []
    buffer_packet = []
    load = []
    for metric in metrics:
        _buffer = []
        _buffer_packet = []
        _load = []
        for individual_simulator in simulator.simulator:
            _buffer_queue, _buffer_size = _get_buffer_size(simulator=individual_simulator, metric=metric)
            _buffer.append(_buffer_size)
            _buffer_packet.append(_buffer_queue)
            _load_percentage = individual_simulator.model.constants['average_bit_rate'] / \
                individual_simulator.model.constants['maximum_bit_rate'] * 100
            if individual_simulator.bidirectional:
                _load.append(_load_percentage / 2)
            else:
                _load.append(_load_percentage)
        buffer.append(_buffer)
        buffer_packet.append(_buffer_packet)
        load.append(_load)
    init()
    fig, ax1 = plt.subplots(1, 1, figsize=(FIG_WIDTH * 1.18, FIG_HEIGHT), dpi=DPI)
    ax2 = ax1.twinx()
    xlabel = "Network Traffic Load ($\%$)"
    if len(metrics) == 1:
        ylabel = _convert_keywords(metric) + " Buffer Size (kB)"
        ylabel2 = _convert_keywords(metric) + " Buffer Size (No. of Packets)"
    else:
        ylabel = "Buffer Size (kB)"
        ylabel2 = "Buffer Size (No. of Packets)"
    for i in range(len(metrics)):
        label = _convert_keywords(metrics[i])
        sns.lineplot(x=load[i], y=buffer[i], lw=0.75, ls='-', marker=markers[i], markersize=MARKERSIZE,
                     markerfacecolor='None', markeredgecolor='k', markeredgewidth=MARKER_EDGE_WIDTH, ax=ax1,
                     color=colors[i], ci=95, label=label)
        sns.lineplot(x=load[i], y=buffer_packet[i], lw=0, markers=False, ax=ax2, ci=None)
    ax1.set_ylabel(ylabel)
    ax2.set_ylabel(ylabel2)
    ax1.set_xlabel(xlabel)
    ax1.grid(which='both')
    if len(metrics) > 1:
        ax1.legend()
    else:
        ax1.legend().set_visible(False)
    if semilog:
        for ax in [ax1, ax2]:
            ax.set_yscale('log')
            ax.minorticks_on()
            ax.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
            ax.ticklabel_format(axis='y', style='plain')
    else:
        for ax in [ax1, ax2]:
            ax.get_xaxis().set_minor_locator(matplotlib.ticker.AutoMinorLocator())
            ax.get_yaxis().set_minor_locator(matplotlib.ticker.AutoMinorLocator())
    ax1.xaxis.grid(True, lw=.5, which='major')
    ax1.yaxis.grid(True, lw=.5, which='major')
    ax1.xaxis.grid(True, lw=.3, which='minor', ls=':')
    ax1.yaxis.grid(True, lw=.3, which='minor', ls=':')
    for ax in [ax1, ax2]:
        ax.tick_params(width=.5, which='major')
        ax.tick_params(width=.3, which='minor')
        for axis in ['top', 'bottom', 'left', 'right']:
            ax.spines[axis].set_linewidth(0.5)
    fig.tight_layout()
    return fig


def _extract_simulators(simulator, data_rate):
    """Function to extractor the simulators with specified data rate.

    Parameters
    ----------
    simulator : ParallelSimulator
        The ParallelSimulator to be unpacked.
    data_rate : float
        Data rate of the simulators to be extracted.

    Returns
    -------
    simulators : list
        A list of simulators with the specified data rate.
    """
    _check_for_ParallelSimulator(simulator)
    simulators = []
    for individual_simulator in simulator.simulator:
        if individual_simulator.model.constants['average_bit_rate'] == data_rate:
            simulators.append(individual_simulator)
    print(str(len(simulators)) + " simulators found.")
    return simulators


def _compute_delay_heatmap(simulators, delay, span):
    """Function to compute the mean delay statistics for the heatmap plot.

    Parameters
    ----------
    simulators : list
        List of BaseSimulator used.
    delay : str
        Type of delay to be computed.

    Returns
    -------
    delay_heatmap : numpy 2d array
        An array of computed mean delay values to be used in the heatmap.

    Raises
    ------
    ValueError
        Raised when inconsistency in simulator node number is found.
    """
    _check_delay_keywords(delay=delay)
    _check_span_keywords(span=span)
    if delay in queueing_delay_keywords:
        delay_type = 'Queueing Delay'
    elif delay in transfer_delay_keywords:
        delay_type = 'Transfer Delay'
    n = simulators[0].model.network.num_nodes
    packet_count = np.zeros([n, n])
    delay_sum = np.zeros([n, n])
    delay_heatmap = np.zeros([n, n])
    delay_heatmap[:] = np.nan
    for simulator in simulators:
        if simulator.model.network.num_nodes != n:
            raise ValueError("Inconsistent number of nodes are found among the simulators.")
        if span in overall_range_keywords:
            latency = simulator.latency
        elif span in extended_range_keywords:
            start_index = simulator.batch_stats[-1]['end_index']
            latency = simulator.latency[start_index:]
        elif span in final_batch_range_keywords:
            start_index = simulator.batch_stats[-1]['start_index']
            end_index = simulator.batch_stats[-1]['end_index']
            latency = simulator.latency[start_index:end_index]
        for latency_dict in latency:
            packet_count[latency_dict['Source ID']][latency_dict['Destination ID']] += 1
            delay_sum[latency_dict['Source ID']][latency_dict['Destination ID']] += latency_dict[delay_type]
    for i in range(n):
        for j in range(n):
            if i != j and packet_count[i][j] > 0:
                delay_heatmap[i][j] = delay_sum[i][j] / packet_count[i][j]
    return delay_heatmap


def plot_delay_heatmap(simulator, data_rate, span='e', delay='td'):
    """Plot mean delay statistics of a specified data rate in a ParallelSimulator.

    Parameters
    ----------
    simulator : ParallelSimulator
        The simulator used.
    data_rate : float
        The chosen data rate.
    span : str, optional
        The time span of the delay statistics in the simulation, by default ``extended``, chosen from the following:

        - `overall` or `all`
            The entire duration of the simulation.
        - `final batch` or `fb`
            The statistics from the final batch when simulation converges.
        - `extended` or `e`
            The extended period of the simulation.
    delay : str, optional
        The type of delay to be plotted, by default ``td``, chosen from the following:

        - `qd`, `queueing delay` or `queueing`
            The overall queueing delay.
        - `td`, `transfer delay` or `transfer`
            The transfer delay.

    Returns
    -------
    fig : Figure
        The figure plotted.
    """
    # Get simulators with the specified
    simulators = _extract_simulators(simulator=simulator, data_rate=data_rate)
    # Compute data to be plotted
    data = _compute_delay_heatmap(simulators=simulators, delay=delay, span=span) / 1000
    # Generate plot
    init()
    fig, ax = plt.subplots(1, 1, figsize=(FIG_WIDTH * 1.1, FIG_HEIGHT * 1.1), dpi=DPI)
    label = 'Average ' + _convert_keywords(delay) + ' ($\mu$s)'
    start, end = 0, len(data)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='3%', pad=0.1)
    sns.heatmap(data=data, cmap='RdBu_r', ax=ax, lw=.125, xticklabels=20, yticklabels=20, square=True, cbar_ax=cax,
                cbar_kws={'shrink': .6, 'pad': .1},)
    ax.set_xlim([start, end])
    ax.set_ylim([end, start])
    ax.set_facecolor('k')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    ax.tick_params(width=.5, which='major')
    cax.tick_params(width=.3, labelsize=5, length=3)
    cax.set_ylabel(label, fontsize=CAX_FONT_SIZE)
    ax.set_xlabel('Destination Node')
    ax.set_ylabel('Source Node')
    frame_linewidth = .5
    ax.axhline(y=start, color='k', linewidth=frame_linewidth)
    ax.axhline(y=end, color='k', linewidth=frame_linewidth)
    ax.axvline(x=start, color='k', linewidth=frame_linewidth)
    ax.axvline(x=end, color='k', linewidth=frame_linewidth)
    ax.set_aspect(1 / ax.get_data_ratio(), adjustable='box')
    fig.tight_layout()
    return fig


def _compute_packet_heatmap(simulators, span):
    """Function to compute the normalised packet number statistics for the heatmap plot.

    Parameters
    ----------
    simulators : list
        List of BaseSimulator used.

    Returns
    -------
    packet_heatmap : numpy 2d array
        An array of computed packet number values to be used in the heatmap.

    Raises
    ------
    ValueError
        Raised when inconsistency in simulator node number is found.
    """
    _check_span_keywords(span=span)
    n = simulators[0].model.network.num_nodes
    packet_count = np.zeros([n, n])
    for simulator in simulators:
        if simulator.model.network.num_nodes != n:
            raise ValueError("Inconsistent number of nodes are found among the simulators.")
        if span in overall_range_keywords:
            latency = simulator.latency
        elif span in extended_range_keywords:
            start_index = simulator.batch_stats[-1]['end_index']
            latency = simulator.latency[start_index:]
        elif span in final_batch_range_keywords:
            start_index = simulator.batch_stats[-1]['start_index']
            end_index = simulator.batch_stats[-1]['end_index']
            latency = simulator.latency[start_index:end_index]
        for latency_dict in latency:
            packet_count[latency_dict['Source ID']][latency_dict['Destination ID']] += 1
    max_packet = np.nanmax(packet_count)
    min_packet = np.nanmin(packet_count)
    for i in range(n):
        for j in range(n):
            if i == j:
                packet_count[i][j] = np.nan
            else:
                packet_count[i][j] = (packet_count[i][j] - min_packet) / (max_packet - min_packet)
    return packet_count


def plot_packet_heatmap(simulator, data_rate, span='e'):
    """Plot mean packet number statistics of a specified data rate in a ParallelSimulator.

    Parameters
    ----------
    simulator : ParallelSimulator
        The simulator used.
    data_rate : float
        The chosen data rate.
    span : str, optional
        The time span of the delay statistics in the simulation, by default ``extended``, chosen from the following:

        - `overall` or `all`
            The entire duration of the simulation.
        - `final batch` or `fb`
            The statistics from the final batch when simulation converges.
        - `extended` or `e`
            The extended period of the simulation.

    Returns
    -------
    fig : Figure
        The figure plotted.
    """
    # Get simulators with the specified
    simulators = _extract_simulators(simulator, data_rate)
    # Compute data to be plotted
    data = _compute_packet_heatmap(simulators=simulators, span=span)
    # Generate plot
    init()
    fig, ax = plt.subplots(1, 1, figsize=(FIG_WIDTH * 1.1, FIG_HEIGHT * 1.1), dpi=DPI)
    label = 'Normalised No. of Packets Transmitted'
    start, end = 0, len(data)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='3%', pad=0.1)
    sns.heatmap(data=data, cmap='RdBu_r', ax=ax, lw=.125, xticklabels=20, yticklabels=20, square=True, cbar_ax=cax,
                cbar_kws={'shrink': .6, 'pad': .1},)
    ax.set_xlim([start, end])
    ax.set_ylim([end, start])
    ax.set_facecolor('k')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    ax.tick_params(width=.5, which='major')
    cax.tick_params(width=.3, labelsize=5, length=3)
    cax.set_ylabel(label, fontsize=CAX_FONT_SIZE)
    ax.set_xlabel('Destination Node')
    ax.set_ylabel('Source Node')
    frame_linewidth = .5
    ax.axhline(y=start, color='k', linewidth=frame_linewidth)
    ax.axhline(y=end, color='k', linewidth=frame_linewidth)
    ax.axvline(x=start, color='k', linewidth=frame_linewidth)
    ax.axvline(x=end, color='k', linewidth=frame_linewidth)
    ax.set_aspect(1 / ax.get_data_ratio(), adjustable='box')
    fig.tight_layout()
    return fig


def plot_ook_ber(snr_min=0, snr_max=15, show_coherent=False):
    """Plot OOK bit error rate vs average energy-to-noise ratio [1]_.

    Parameters
    ----------
    snr_max : int, optional
        Maximum energy-to-noise ratio value in dB, by default ``15``.
    show_coherent : bool, optional
        If coherent detection is shown, by default ``False``.

    Returns
    -------
    fig : Figure
        The figure plotted.

    References
    ----------
    .. [1] Tang, Qinghui, Sandeep KS Gupta, and Loren Schwiebert. "BER performance analysis of an on-off keying \
         based minimum energy coding for energy constrained wireless sensor applications." \
         In IEEE International Conference on Communications, 2005. \
         ICC 2005. 2005, vol. 4, pp. 2734-2738. IEEE, 2005.
    """
    # Compute values
    SNR_MIN = snr_min
    SNR_MAX = snr_max
    Eb_No_dB = np.linspace(SNR_MIN, SNR_MAX, 10000)
    Eb_No = 10**(Eb_No_dB / 10.0)
    sigma = 0.1
    a = 4 * Eb_No
    b_th = sigma * np.sqrt(2 + Eb_No)
    sigma = b_th / np.sqrt(2 + Eb_No)
    b = (b_th / sigma) * (b_th / sigma)
    pes = np.exp(-b_th * b_th / (2 * sigma * sigma))
    pem = 1 - (ncx2.sf(x=b, df=2, nc=a))
    ook_non_coherent = 0.5 * (pem + pes)
    ook_coherent = 0.5 * erfc(np.sqrt(Eb_No / 2))
    # Generate plot
    init()
    fig, ax = plt.subplots(1, 1, figsize=(FIG_WIDTH, FIG_HEIGHT), dpi=DPI)
    xlabel = "$E_b/N_o$ (dB)"
    ylabel = "BER"
    labels = ["Noncoherent", "Coherent"]
    sns.lineplot(x=Eb_No_dB, y=ook_non_coherent, lw=0.75, markers=False,
                 ax=ax, ci=None, color=colors[0], label=labels[0])
    if show_coherent:
        sns.lineplot(x=Eb_No_dB, y=ook_coherent, lw=0.75, markers=False,
                     ax=ax, ci=None, color=colors[-1], label=labels[1])
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.grid(which='both')
    ax.set_yscale('log')
    ax.minorticks_on()
    if not show_coherent:
        ax.legend().set_visible(False)
    ax.xaxis.grid(True, lw=.5, which='major')
    ax.yaxis.grid(True, lw=.5, which='major')
    ax.xaxis.grid(True, lw=.3, which='minor', ls=':')
    ax.yaxis.grid(True, lw=.3, which='minor', ls=':')
    ax.tick_params(width=.5, which='major')
    ax.tick_params(width=.3, which='minor')
    for axis in ['top', 'bottom', 'left', 'right']:
        ax.spines[axis].set_linewidth(0.5)
    ax.set_aspect(1 / ax.get_data_ratio(), adjustable='box')
    fig.tight_layout()
    return fig


def _compute_scaled_network_transfer_delay(data_type):
    """Function to compute the data to be plotted in a scaled network.

    Parameters
    ----------
    data_type : str
        The type of data to be plotted.

    Returns
    -------
    x : list
        A list of x values to be plotted.
    y : list
        A list of y values to be plotted.
    labels : list
        A list of y labels.
    """
    _check_scaled_network_keywords(data_type=data_type)
    transfer_delay = []
    if data_type in load_keywards:
        load_list = [10, 15, 20, 25]
        num_nodes_list = np.arange(100, 11100, 1000)
    elif data_type in scale_keywords:
        load_list = np.arange(1, 44, 1)
        num_nodes_list = [512, 1280, 5120, 10240]
    for j in range(len(num_nodes_list)):
        num_nodes = num_nodes_list[j]
        length = num_nodes * 1.2
        network = Network(length=length, num_nodes=num_nodes)
        model = Model(network=network)
        _transfer_delay = []
        for i in range(len(load_list)):
            model.constants['average_bit_rate'] = load_list[i]
            simulator = BaseSimulator(convergence=True, model=model)
            _transfer_delay.append(get_transfer_delay(simulator=simulator) / 1000)
            if np.isinf(_transfer_delay[-1]):
                _transfer_delay[-1] = np.nan
        transfer_delay.append(_transfer_delay)
    if data_type in load_keywards:
        x = num_nodes_list
        y = list(map(list, zip(*transfer_delay)))
        labels = [str(item) + "\%" for item in load_list]
    elif data_type in scale_keywords:
        x = load_list
        y = transfer_delay
        labels = [str(item) for item in num_nodes_list]
    return x, y, labels


def plot_scaled_network_delay(data_type='load'):
    """Plot delay of a scaled network.

    Parameters
    ----------
    data_type : str, optional
        The data of focus, chosen from the following:

        - `load` or `l`: Varying load of the network at 10%, 15%, 20% and 25% for \
            network node number from 100 to 10100.
        - `scale`or `s`: Varying number of nodes in the network at 512, 1280, 5120, and 10240 \
            for network traffic load from 1% to 40$.

        Default is ``load``.

    Returns
    -------
    fig : Figure
        The figure plotted.
    """
    x, y, labels = _compute_scaled_network_transfer_delay(data_type=data_type)
    init()
    fig, ax = plt.subplots(1, 1, figsize=(FIG_WIDTH, FIG_HEIGHT), dpi=DPI)
    xlabel = ""
    ylabel = "Analytical Average Transfer Delay ($\mu$s)"
    for i in range(len(y)):
        sns.lineplot(x=x, y=y[i], lw=0.75, ls='-', marker=markers[i], markersize=MARKERSIZE,
                     markerfacecolor='None', markeredgecolor='k', markeredgewidth=MARKER_EDGE_WIDTH, ax=ax,
                     color=colors[i], label=labels[i], zorder=len(y) - i)
    ax.grid(which='both')
    if data_type in scale_keywords:
        ax.set_yscale('log')
        ylim = np.power(10, int(np.log10(np.nanmax(y))) + 1)
        ax.set_ylim(top=ylim)
        xlabel = "Network Traffic Load (\%)"
    elif data_type in load_keywards:
        ax.get_xaxis().set_minor_locator(matplotlib.ticker.AutoMinorLocator())
        ax.get_yaxis().set_minor_locator(matplotlib.ticker.AutoMinorLocator())
        xlabel = "Number of Nodes"
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.legend(loc='upper left')
    ax.xaxis.grid(True, lw=.5, which='major')
    ax.yaxis.grid(True, lw=.5, which='major')
    ax.xaxis.grid(True, lw=.3, which='minor', ls=':')
    ax.yaxis.grid(True, lw=.3, which='minor', ls=':')
    ax.tick_params(width=.5, which='major')
    ax.tick_params(width=.3, which='minor')
    for axis in ['top', 'bottom', 'left', 'right']:
        ax.spines[axis].set_linewidth(0.5)
    ax.set_aspect(1 / ax.get_data_ratio(), adjustable='box')
    fig.tight_layout()
    return fig
