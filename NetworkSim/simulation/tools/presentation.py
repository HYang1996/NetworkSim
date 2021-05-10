__author__ = ['Hongyi Yang']
__all__ = [
    'init',
    'save_data',
    'load_data',
    'load_and_save_delay_heatmap_data',
    'load_and_save_delay_data',
    'load_and_save_throughput_data',
    'load_and_save_buffer_data',
    'plot_and_save_delay_heatmap',
    'plot_delay_heatmap_at_load',
    'convert_analytical_simulation_delay_data_to_df',
    'convert_min_mean_max_delay_data_to_df',
    'plot_delay',
    'convert_buffer_data_to_df',
    'plot_buffer',
    'convert_throughput_data_to_df',
    'plot_throughput',
    'convert_scaled_network_delay_to_df',
    'plot_scaled_network_delay',
    'plot_ber_snr'
]

import numpy as np
import os
import pickle
import bz2
import gc
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import rc
from matplotlib.ticker import ScalarFormatter, AutoMinorLocator
from mpl_toolkits.axes_grid1 import make_axes_locatable
import warnings
import imageio
import pandas as pd
from scipy.stats import ncx2

from NetworkSim.simulation.tools.load_save import load_model
from NetworkSim.simulation.tools.performance_analysis import \
    get_transfer_delay, get_queueing_delay, get_min_transfer_delay, get_service_delay, \
    get_extended_run_delay, get_overall_delay, get_extended_run_throughput, get_overall_throughput
from NetworkSim.simulation.tools.publication import _compute_scaled_network_transfer_delay

queueing_delay_keywords = {'queueing delay', 'qd', 'queueing'}
transfer_delay_keywords = {'transfer delay', 'td', 'transfer'}

overall_range_keywords = {'overall', 'all'}
extended_range_keywords = {'extended', 'e'}

unidirectional_keywords = {'uni', 'unidirectional'}
bidirectional_keywords = {'bi', 'bidirectional'}

load_keywards = {'load', 'l'}
scale_keywords = {'scale', 's'}

vmin_max = {
    'uni_td_all_delay_heatmap': [0.2, 1.8],
    'uni_qd_all_delay_heatmap': [0, 1.6],
    'bi_td_all_delay_heatmap': [0.2, 1.8],
    'bi_qd_all_delay_heatmap': [0, 1.6],
}

FIG_WIDTH = 3
FIG_HEIGHT = 3
MARKERSIZE = 4
MARKER_EDGE_WIDTH = .4
DPI = 600
CAX_FONT_SIZE = 6


def init():
    """
    Plot environment initialisation.
    """
    gc.collect()
    sns.set_theme(style="ticks")
    sns.set_context("paper")
    SMALLER_SIZE = 6
    SMALL_SIZE = 7
    MEDIUM_SIZE = 8
    LARGE_SIZE = 9
    BIGGER_SIZE = 10
    rc('font', **{'family': 'serif', 'serif': ['Fira Code']})
    rc('font', size=SMALL_SIZE)          # controls default text sizes
    rc('axes', titlesize=LARGE_SIZE)     # fontsize of the axes title
    rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
    rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    rc('legend', fontsize=SMALLER_SIZE)  # legend fontsize
    rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
    sns.set_palette('icefire')
#     sns.set_palette('mako')
    warnings.filterwarnings("ignore")


def save_data(data, fname, dir_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    load_dir = os.path.join(dir_path, '../../../animations', dir_name)
    os.chdir(load_dir)
    file_output = bz2.BZ2File(fname, 'w')
    pickle.dump(data, file_output)
    os.chdir(dir_path)
    print(fname, "saved.")


def load_data(dir_name, fname):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    load_dir = os.path.join(dir_path, '../../../animations', dir_name)
    os.chdir(load_dir)
    file_input = bz2.BZ2File(fname, 'rb')
    data = pickle.load(file_input)
    os.chdir(dir_path)
    print(fname, 'loaded.')
    return data


def load_and_save_delay_heatmap_data():
    delay_types = ['Transfer Delay', 'Queueing Delay']
    ring_types = ['uni', 'bi']
    time_spans = ['all', 'extended']

    def get_fname(delay, ring, span):
        fname = ring + "_"
        if delay == 'Transfer Delay':
            fname = fname + 'td_' + span
        else:
            fname = fname + 'qd_' + span
        return fname

    for delay_type in delay_types:
        for ring_type in ring_types:
            for span in time_spans:
                # Initialise variables
                delay_heatmap_data = []
                # Iterate through simulations
                if ring_type in unidirectional_keywords:
                    start, end, interval = 1, 41, 1
                elif ring_type in bidirectional_keywords:
                    start, end, interval = 2, 82, 2
                for k in range(start, end, interval):
                    n = 100
                    packet_count = np.zeros([n, n])
                    delay_sum = np.zeros([n, n])
                    delay_heatmap = np.zeros([n, n])
                    delay_heatmap[:] = np.nan
                    # Compute delay heatmap data
                    for i in range(1, 11):
                        fname = ring_type + "-load_" + str(k) + "-seed_" + str(i)
                        simulator = load_model(fname=fname)[0]
                        if span in overall_range_keywords:
                            latency = simulator.latency
                        elif span in extended_range_keywords:
                            start_index = simulator.batch_stats[-1]['end_index']
                            latency = simulator.latency[start_index:]
                        for latency_dict in latency:
                            packet_count[latency_dict['Source ID']][latency_dict['Destination ID']] += 1
                            delay_sum[latency_dict['Source ID']
                                      ][latency_dict['Destination ID']] += latency_dict[delay_type]
                    for i in range(n):
                        for j in range(n):
                            if i != j and packet_count[i][j] > 0:
                                delay_heatmap[i][j] = delay_sum[i][j] / packet_count[i][j]
                    delay_heatmap_data.append(delay_heatmap / 1000)
                # Save delay heatmap data
                data_fname = get_fname(delay=delay_type, ring=ring_type, span=span) + '_delay_heatmap'
                save_data(data=delay_heatmap_data, fname=data_fname, dir_name='delay_heatmap_data')


def load_and_save_delay_data():
    ring_types = ['uni', 'bi']
    # Iterate through simulations
    for ring_type in ring_types:
        # Initialise variables
        delay_data = {}
        analytical_transfer_delay = []
        analytical_queueing_delay = []
        analytical_min_transfer_delay = []
        simulation_overall_delay = []
        simulation_extended_delay = []
        if ring_type in unidirectional_keywords:
            start, end, interval = 1, 41, 1
        elif ring_type in bidirectional_keywords:
            start, end, interval = 2, 82, 2
        for k in range(start, end, interval):
            # Append delay data
            for i in range(1, 11):
                fname = ring_type + "-load_" + str(k) + "-seed_" + str(i)
                simulator = load_model(fname=fname)[0]
                simulation_overall_delay.append(get_overall_delay(simulator=simulator))
                simulation_extended_delay.append(get_extended_run_delay(simulator=simulator))
            analytical_queueing_delay.append(get_queueing_delay(simulator=simulator) +
                                             get_service_delay(simulator=simulator))
            analytical_transfer_delay.append(get_transfer_delay(simulator=simulator))
            analytical_min_transfer_delay.append(get_min_transfer_delay(simulator=simulator))
        delay_data['simulation_overall'] = simulation_overall_delay
        delay_data['simulation_extended'] = simulation_extended_delay
        delay_data['analytical_queueing'] = analytical_queueing_delay
        delay_data['analytical_transfer'] = analytical_transfer_delay
        delay_data['analytical_min_transfer'] = analytical_min_transfer_delay
        # Save delay data
        data_fname = ring_type + '_delay_data'
        save_data(data=delay_data, fname=data_fname, dir_name='delay_data')


def load_and_save_throughput_data():
    ring_types = ['uni', 'bi']
    # Iterate through simulations
    for ring_type in ring_types:
        # Initialise variables
        throughput_data = {}
        overall_throughput = []
        extended_throughput = []
        if ring_type in unidirectional_keywords:
            start, end, interval = 1, 41, 1
        elif ring_type in bidirectional_keywords:
            start, end, interval = 2, 82, 2
        for k in range(start, end, interval):
            # Append delay data
            for i in range(1, 11):
                fname = ring_type + "-load_" + str(k) + "-seed_" + str(i)
                simulator = load_model(fname=fname)[0]
                overall_throughput.append(get_overall_throughput(simulator=simulator))
                extended_throughput.append(get_extended_run_throughput(simulator=simulator))
        throughput_data['overall'] = overall_throughput
        throughput_data['extended'] = extended_throughput
        # Save delay data
        data_fname = ring_type + '_throughput_data'
        save_data(data=throughput_data, fname=data_fname, dir_name='throughput_data')


def load_and_save_buffer_data():
    ring_types = ['uni', 'bi']
    # Iterate through simulations
    for ring_type in ring_types:
        # Initialise variables
        buffer_data = {}
        mean_size = []
        max_size = []
        if ring_type in unidirectional_keywords:
            start, end, interval = 1, 41, 1
        elif ring_type in bidirectional_keywords:
            start, end, interval = 2, 82, 2
        for k in range(start, end, interval):
            # Append delay data
            for i in range(1, 11):
                fname = ring_type + "-load_" + str(k) + "-seed_" + str(i)
                simulator = load_model(fname=fname)[0]
                mean_queue_size, max_queue_size, _ = simulator.summary(summary_type='q')
                mean_size.append(mean_queue_size)
                max_size.append(max_queue_size)
        buffer_data['mean'] = mean_size
        buffer_data['max'] = max_size
        # Save delay data
        data_fname = ring_type + '_buffer_data'
        save_data(data=buffer_data, fname=data_fname, dir_name='buffer_data')


def plot_and_save_delay_heatmap(delay_heatmap_data, fname, delay='td', gif=True, load_max=35):
    images = []
    # Plot and save images
    for i in range(0, load_max, 1):
        init()
        data = delay_heatmap_data[i]
        fig, ax = plt.subplots(1, 1, figsize=(FIG_WIDTH * 1.1, FIG_HEIGHT * 1.1), dpi=DPI)
        if delay in transfer_delay_keywords:
            label = "Average Trasnfer Delay ($\mu$s)"
        elif delay in queueing_delay_keywords:
            label = "Average Queueing Delay ($\mu$s)"
        else:
            raise ValueError("Delay type not recognised.")
        start, end = 0, len(data)
        if fname in vmin_max:
            vmin, vmax = vmin_max[fname][0], vmin_max[fname][1]
        else:
            vmin, vmax = None, None
        divider = make_axes_locatable(ax)
        cax = divider.append_axes('right', size='3%', pad=0.1)
        sns.heatmap(data=data, cmap='icefire', ax=ax, lw=0, xticklabels=20, yticklabels=20, square=True, cbar_ax=cax,
                    cbar_kws={'shrink': .6, 'pad': .1}, vmin=vmin, vmax=vmax)
        ax.set_xlim([start, end])
        ax.set_ylim([end, start])
        ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
        ax.tick_params(width=.5, which='major')
        cax.tick_params(width=.3, labelsize=5, length=3)
        cax.set_yticklabels(cax.get_yticklabels(), rotation=0)
        cax.set_ylabel(label, fontsize=CAX_FONT_SIZE)
        ax.set_xlabel('Destination Node')
        ax.set_ylabel('Source Node')
        frame_linewidth = .5
        ax.axhline(y=start, color='k', linewidth=frame_linewidth)
        ax.axhline(y=end, color='k', linewidth=frame_linewidth)
        ax.axvline(x=start, color='k', linewidth=frame_linewidth)
        ax.axvline(x=end, color='k', linewidth=frame_linewidth)
        ax.set_title(f'{i + 1}% Network Loading')
        ax.set_aspect(1 / ax.get_data_ratio(), adjustable='box')
        fig.tight_layout()
        fig_fname = fname + '_' + str(i + 1)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        load_dir = os.path.join(dir_path, '../../../animations', fname)
        os.chdir(load_dir)
        plt.savefig(fig_fname)
        os.chdir(dir_path)
        if gif:
            images.append(imageio.imread(os.path.join(load_dir, fig_fname + '.png')))
    # Generate GIF
    if gif:
        os.chdir(load_dir)
        imageio.mimsave(fname + '.gif', images, fps=5)
        os.chdir(dir_path)


def plot_delay_heatmap_at_load(delay_heatmap_data, load, delay='td'):
    init()
    data = delay_heatmap_data[load - 1]
    fig, ax = plt.subplots(1, 1, figsize=(FIG_WIDTH * 1.1, FIG_HEIGHT * 1.1), dpi=DPI)
    if delay in transfer_delay_keywords:
        label = "Average Trasnfer Delay ($\mu$s)"
    elif delay in queueing_delay_keywords:
        label = "Average Queueing Delay ($\mu$s)"
    else:
        raise ValueError("Delay type not recognised.")
    start, end = 0, len(data)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='3%', pad=0.1)
    sns.heatmap(data=data, cmap='icefire', ax=ax, lw=0, xticklabels=20, yticklabels=20,
                square=True, cbar_ax=cax, cbar_kws={'shrink': .6, 'pad': .1})
    ax.set_xlim([start, end])
    ax.set_ylim([end, start])
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    ax.tick_params(width=.5, which='major')
    cax.tick_params(width=.3, labelsize=5, length=3)
    cax.set_yticklabels(cax.get_yticklabels(), rotation=0)
    cax.set_ylabel(label, fontsize=CAX_FONT_SIZE)
    ax.set_xlabel('Destination Node')
    ax.set_ylabel('Source Node')
    frame_linewidth = .5
    ax.axhline(y=start, color='k', linewidth=frame_linewidth)
    ax.axhline(y=end, color='k', linewidth=frame_linewidth)
    ax.axvline(x=start, color='k', linewidth=frame_linewidth)
    ax.axvline(x=end, color='k', linewidth=frame_linewidth)
    ax.set_title(f'{load}% Network Loading')
    ax.set_aspect(1 / ax.get_data_ratio(), adjustable='box')
    fig.tight_layout()
    return fig


def convert_analytical_simulation_delay_data_to_df(delay_data, delay):
    if delay in transfer_delay_keywords:
        keys = ['analytical_transfer', 'mean_transfer_delay']
    elif delay in queueing_delay_keywords:
        keys = ['analytical_queueing', 'mean_queueing_delay']
    else:
        raise ValueError("Delay type not recognised")
    df_analytical = pd.DataFrame()
    df_analytical['load'] = np.linspace(1, 40, 40).tolist()
    df_analytical['delay'] = [x / 1000 for x in delay_data[keys[0]]]
    df_analytical['label'] = np.repeat('Analytical', 40).tolist()
    df_mean = pd.DataFrame()
    df_mean['load'] = np.repeat(np.linspace(1, 40, 40), 10).tolist()
    df_mean['delay'] = [delay[keys[1]] / 1000 for delay in delay_data['simulation_extended']]
    df_mean['label'] = np.repeat('Simulation', 400).tolist()
    return pd.concat([df_analytical, df_mean])


def convert_min_mean_max_delay_data_to_df(delay_data):
    keys = ['min_transfer_delay', 'mean_transfer_delay', 'max_transfer_delay', 'analytical_min_td']
    df_min = pd.DataFrame()
    df_mean = pd.DataFrame()
    df_max = pd.DataFrame()
    df_analytical_min = pd.DataFrame()
    df_min['load'] = np.repeat(np.linspace(1, 40, 40), 10).tolist()
    df_mean['load'] = np.repeat(np.linspace(1, 40, 40), 10).tolist()
    df_max['load'] = np.repeat(np.linspace(1, 40, 40), 10).tolist()
    df_analytical_min['load'] = np.linspace(1, 40, 40).tolist()
    df_min['delay'] = [delay[keys[0]] / 1000 for delay in delay_data['simulation_extended']]
    df_mean['delay'] = [delay[keys[1]] / 1000 for delay in delay_data['simulation_extended']]
    df_max['delay'] = [delay[keys[2]] / 1000 for delay in delay_data['simulation_extended']]
    df_analytical_min['delay'] = [x / 1000 for x in delay_data['analytical_min_transfer']]
    df_min['label'] = np.repeat('Minimum', 400).tolist()
    df_mean['label'] = np.repeat('Average', 400).tolist()
    df_max['label'] = np.repeat('Maximum', 400).tolist()
    df_analytical_min['label'] = np.repeat('Theoretical Minimum', 40).tolist()
    return pd.concat([df_min, df_mean, df_max, df_analytical_min])


def plot_delay(data, delay='td', plot_type=1):
    if plot_type == 'as' or plot_type == 1:
        data_df = convert_analytical_simulation_delay_data_to_df(delay_data=data, delay=delay)
        if delay in transfer_delay_keywords:
            ylabel = "Average Trasnfer Delay ($\mu$s)"
        elif delay in queueing_delay_keywords:
            ylabel = "Average Queueing Delay ($\mu$s)"
    elif plot_type == '3m' or plot_type == 2:
        data_df = convert_min_mean_max_delay_data_to_df(delay_data=data)
        ylabel = "Transfer Delay ($\mu$s)"
    init()
    fig, ax = plt.subplots(1, 1, figsize=(FIG_WIDTH * 1.05, FIG_HEIGHT), dpi=DPI)
    xlabel = "Network Traffic Load ($\%$)"

    sns.lineplot(data=data_df, x='load', y='delay', hue='label', style='label', ax=ax, lw=.75, markersize=MARKERSIZE,
                 markeredgewidth=MARKER_EDGE_WIDTH, markers=True, dashes=True, alpha=.7, ci=95, palette='icefire')
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.legend_.set_title(None)
    ax.grid(which='both')
    ax.set_yscale('log')
    ax.minorticks_on()
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


def convert_buffer_data_to_df(buffer_data):
    df_mean = pd.DataFrame()
    df_max = pd.DataFrame()
    df_mean['load'] = np.repeat(np.linspace(1, 40, 40), 10).tolist()
    df_max['load'] = np.repeat(np.linspace(1, 40, 40), 10).tolist()
    df_mean['size'] = buffer_data['mean']
    df_mean['size_kB'] = [x * 1.5 for x in buffer_data['mean']]
    df_max['size'] = buffer_data['max']
    df_max['size_kB'] = [x * 1.5 for x in buffer_data['max']]
    df_mean['label'] = np.repeat('Average', 400).tolist()
    df_max['label'] = np.repeat('Maximum', 400).tolist()
    return pd.concat([df_mean, df_max])


def plot_buffer(data):
    data_df = convert_buffer_data_to_df(buffer_data=data)
    init()
    fig, ax1 = plt.subplots(1, 1, figsize=(FIG_WIDTH * 1.18, FIG_HEIGHT), dpi=DPI)
    ax2 = ax1.twinx()
    xlabel = "Network Traffic Load ($\%$)"
    ylabel = "Buffer Size (kB)"
    ylabel2 = "Buffer Size (No. of Packets)"
    sns.lineplot(data=data_df, x='load', y='size_kB', hue='label', style='label', ax=ax1, lw=.75,
                 markersize=MARKERSIZE, markeredgewidth=MARKER_EDGE_WIDTH, markers=True,
                 dashes=True, alpha=.7, ci=95, palette='icefire')
    sns.lineplot(data=data_df, x='load', y='size', hue='label', style='label', lw=0, markers=False, ax=ax2, ci=None)
    ax1.set_ylabel(ylabel)
    ax2.set_ylabel(ylabel2)
    ax1.set_xlabel(xlabel)
    ax1.grid(which='both')
    ax1.legend_.set_title(None)
    ax2.legend().set_visible(False)
    for ax in [ax1, ax2]:
        ax.set_yscale('log')
        ax.minorticks_on()
        ax.yaxis.set_major_formatter(ScalarFormatter())
        ax.ticklabel_format(axis='y', style='plain')
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


def convert_throughput_data_to_df(throughput_data, ring_type):
    df = pd.DataFrame()
    if ring_type in unidirectional_keywords:
        df['load'] = np.repeat(np.linspace(.1, 4, 40), 10).tolist()
    elif ring_type in bidirectional_keywords:
        df['load'] = np.repeat(np.linspace(.2, 8, 40), 10).tolist()
    df['throughput'] = [x / 1000 for x in throughput_data['extended']]
    return df


def plot_throughput(data, ring_type):
    data_df = convert_throughput_data_to_df(throughput_data=data, ring_type=ring_type)
    init()
    fig, ax = plt.subplots(1, 1, figsize=(FIG_WIDTH, FIG_HEIGHT), dpi=DPI)
    xlabel = "Network Traffic Load (Tbit/s)"
    ylabel = "Average Throughput (Tbit/s)"
    sns.lineplot(data=data_df, x='load', y='throughput', ax=ax, lw=.75,
                 markersize=MARKERSIZE, markeredgewidth=MARKER_EDGE_WIDTH, marker='X',
                 dashes=True, ci=95, palette='icefire')
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.grid(which='both')
    ax.get_xaxis().set_minor_locator(AutoMinorLocator())
    ax.get_yaxis().set_minor_locator(AutoMinorLocator())
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


def convert_scaled_network_delay_to_df(data_type):
    x, y, labels = _compute_scaled_network_transfer_delay(data_type=data_type)
    if data_type in load_keywards:
        labels = ['10%', '15%', '20%', '25%']
    df = None
    for i in range(len(y)):
        df_temp = pd.DataFrame()
        df_temp['x'] = x
        df_temp['y'] = y[i]
        df_temp['label'] = np.repeat(labels[i], len(x)).tolist()
        if df is None:
            df = df_temp.copy()
        else:
            df = pd.concat([df, df_temp])
    return df


def plot_scaled_network_delay(data_type):
    data_df = convert_scaled_network_delay_to_df(data_type=data_type)
    init()
    fig, ax = plt.subplots(1, 1, figsize=(FIG_WIDTH, FIG_HEIGHT), dpi=DPI)
    xlabel = ""
    ylabel = "Analytical Average Transfer Delay ($\mu$s)"
    sns.lineplot(data=data_df, x='x', y='y', hue='label', style='label', ax=ax, lw=.75,
                 markersize=MARKERSIZE, markeredgewidth=MARKER_EDGE_WIDTH, markers=True,
                 dashes=True, alpha=.7, ci=95, palette='icefire')
    ax.grid(which='both')
    if data_type in scale_keywords:
        ax.set_yscale('log')
        ylim = np.power(10, int(np.log10(np.nanmax(data_df['y']))) + 1)
        ax.set_ylim(top=ylim)
        xlabel = "Network Traffic Load (%)"
        title = "Number of Nodes Superimposed"
    elif data_type in load_keywards:
        ax.get_xaxis().set_minor_locator(AutoMinorLocator())
        ax.get_yaxis().set_minor_locator(AutoMinorLocator())
        xlabel = "Number of Nodes"
        title = "Network Loading Superimposed"
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.legend(loc='upper left')
    ax.set_title(title)
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


def plot_ber_snr():
    SNR_MIN = 0
    SNR_MAX = 18.3
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
    # Generate plot
    init()
    fig, ax = plt.subplots(1, 1, figsize=(FIG_WIDTH, FIG_HEIGHT), dpi=DPI)
    xlabel = "$\mathregular{E_b/N_o}$ (dB)"
    ylabel = "BER"
    sns.lineplot(x=Eb_No_dB, y=ook_non_coherent, ax=ax, lw=.75, palette='icefire')
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.grid(which='both')
    ax.set_yscale('log')
    ax.minorticks_on()
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
