"""
Utilities for calculating network performance analysis
"""

__all__ = [
    "get_service_delay",
    "get_transfer_delay",
    "get_queueing_delay",
    "get_final_batch_delay",
    "get_extended_run_delay",
    "get_overall_delay",
    "get_final_batch_throughput",
    "get_extended_run_throughput",
    "get_overall_throughput"
]
__author__ = ["Hongyi Yang"]

import numpy as np


def get_service_delay(simulator):
    """
    Function to compute the service delay latency of the defined network.

    The service delay is defined from the moment a data packet is at the head of the transmittor buffer queue \
        to the moment when the packet is fully transmitted.

    Parameters
    ----------
    simulator : BaseSimulator
        The simulator used to create the network.

    Returns
    -------
    service_delay : float
        The estimated average service delay latency of the network.
    """
    t_t = simulator.model.constants.get('tuning_time')
    t_s = simulator.model.circulation_time / simulator.model.max_data_packet_num_on_ring
    N = simulator.model.network.num_nodes
    lambda_a = simulator.model.constants.get('average_bit_rate') / simulator.model.data_signal.size / 8
    if simulator.bidirectional:
        lambda_a /= 2
    W = simulator.model.network.num_nodes
    service_delay = t_s / 2 + t_t * (N - 1) / N + (t_s * t_s * N * lambda_a) / (2 * W - t_s * N * lambda_a)
    return service_delay


def get_queueing_delay(simulator):
    """
    Function to compute the queueing delay latency of the defined network.

    The queueing delay is defined from the source traffic generation, when the generated data packets \
        arrive at the transmittor buffer queue, to the moment when the data packets reach the head of the queue.

    Parameters
    ----------
    simulator : BaseSimulator
        The simulator used to create the network.

    Returns
    -------
    queueing_delay : float
        The estimated average queueing delay latency of the network.
    """
    t_s = simulator.model.circulation_time / simulator.model.max_data_packet_num_on_ring
    lambda_a = simulator.model.constants.get('average_bit_rate') / simulator.model.data_signal.size / 8
    if simulator.bidirectional:
        lambda_a /= 2
    service_delay = get_service_delay(simulator=simulator)
    queueing_delay = .5 * t_s / (1 - lambda_a * t_s - lambda_a * service_delay)
    if queueing_delay < 0:
        queueing_delay = np.inf
    return queueing_delay


def get_transfer_delay(simulator, include_pd=True):
    """
    Function to compute the transfer delay latency of the defined network.

    Parameters
    ----------
    simulator : BaseSimulator
        The simulator used to create the network.
    include_pd : bool
        If propagation delay is considered. Default is ``True``.

    Returns
    -------
    transfer_delay : float
        The estimated average transfer delay latency of the network.
    """
    if include_pd:
        t_pd = simulator.model.circulation_time
    else:
        t_pd = 0
    t_tr = simulator.model.data_packet_duration
    if simulator.bidirectional:
        transfer_delay = get_queueing_delay(simulator=simulator) + \
            get_service_delay(simulator=simulator) + t_tr + t_pd / 4
    else:
        transfer_delay = get_queueing_delay(simulator=simulator) + \
            get_service_delay(simulator=simulator) + t_tr + t_pd / 2
    return transfer_delay


def get_min_transfer_delay(simulator):
    """
    Function to compute the theoretical average minimum transfer delay latency.

    Parameters
    ----------
    simulator : BaseSimulator
        The simulator used.

    Returns
    -------
    min_transfer_delay : float
        The theoretical minimum transfer delay.
    """
    t_tr = simulator.model.data_packet_duration
    interval_length = simulator.model.network.get_interval()
    time_of_flight = interval_length / simulator.model.constants['speed'] * 1e9
    min_transfer_delay = t_tr + time_of_flight
    return min_transfer_delay


def get_final_batch_delay(simulator):
    """Function to compute mean queueing and transfer delay of the final batch in the simulation.

    Parameters
    ----------
    simulator : BaseSimulator
        The simulator used.

    Returns
    -------
    results : dict
        A dictionary containing the following:

        - `min_queueing_delay` : minimum queueing delay
        - `max_queueing_delay` : maximum queueing delay
        - `mean_queueing_delay` : mean queueing delay
        - `min_transfer_delay` : minimum transfer delay
        - `max_transfer_delay` : maximum transfer delay
        - `mean_transfer_delay` : mean transfer delay

    Raises
    ------
    NotImplementedError
        Raised when convergence mode is disabled for the simulator.
    """
    # Check if convergence mode is enabled
    if not simulator.convergence:
        raise NotImplementedError("Final batch delay calculation is only applicable for convergence mode.")
    # Extract statistics of final batch
    stats = simulator.batch_stats[-1]
    start = stats['start_index']
    end = stats['end_index']
    latency_batch = simulator.latency[start:end]
    results = _get_delay_results(simulator=simulator, latency=latency_batch)
    return results


def get_extended_run_delay(simulator):
    """Function to compute mean queueing and transfer delay of the extended run.

    Parameters
    ----------
    simulator : BaseSimulator
        The simulator used.

    Returns
    -------
    results : dict
        A dictionary containing the following:

        - `min_queueing_delay` : float
            minimum queueing delay
        - `max_queueing_delay` : float
            maximum queueing delay
        - `mean_queueing_delay` : float
            mean queueing delay
        - `min_transfer_delay` : float
            minimum transfer delay
        - `max_transfer_delay` : float
            maximum transfer delay
        - `mean_transfer_delay` : float
            mean transfer delay

    Raises
    ------
    NotImplementedError
        Raised when convergence mode is disabled for the simulator.
    ValueError
        Raised when extended run is disabled for the simulator.
    """
    # Check if convergence mode is enabled
    if not simulator.convergence:
        raise NotImplementedError("Extended run delay calculation is only applicable for convergence mode.")
    # Check if extended run is enabled
    elif not simulator.extended:
        raise ValueError("Extended run is disabled for the simulator.")
    start = simulator.batch_stats[-1]['end_index']
    latency_batch = simulator.latency[start:]
    results = _get_delay_results(simulator=simulator, latency=latency_batch)
    return results


def get_overall_delay(simulator):
    """Function to compute the mean queueing and transfer delay of a simulation.

    Parameters
    ----------
    simulator : BaseSimulator
        The simulator used.

    Returns
    -------
    results : dict
        A dictionary containing the following:

        - `min_queueing_delay` : float
            minimum queueing delay
        - `max_queueing_delay` : float
            maximum queueing delay
        - `mean_queueing_delay` : float
            mean queueing delay
        - `min_transfer_delay` : float
            minimum transfer delay
        - `max_transfer_delay` : float
            maximum transfer delay
        - `mean_transfer_delay` : float
            mean transfer delay
    """
    latency = simulator.latency
    results = _get_delay_results(simulator=simulator, latency=latency)
    return results


def _get_delay_results(simulator, latency):
    """Function to compute delay statistics of a given latency list.

    Parameters
    ----------
    latency : list
        A list of latency information.
    simulator : BaseSimulator
        The simulator used.

    Returns
    -------
    results : dict
        A dictionary containing the following:

        - `min_queueing_delay` : float
            minimum queueing delay
        - `max_queueing_delay` : float
            maximum queueing delay
        - `mean_queueing_delay` : float
            mean queueing delay
        - `min_transfer_delay` : float
            minimum transfer delay
        - `max_transfer_delay` : float
            maximum transfer delay
        - `mean_transfer_delay` : float
            mean transfer delay
    """
    results = {}
    latency = simulator.latency
    results['min_queueing_delay'] = np.min(list(item['Queueing Delay'] for item in latency))
    results['max_queueing_delay'] = np.max(list(item['Queueing Delay'] for item in latency))
    results['mean_queueing_delay'] = np.mean(list(item['Queueing Delay'] for item in latency))
    results['min_transfer_delay'] = np.min(list(item['Transfer Delay'] for item in latency))
    results['max_transfer_delay'] = np.max(list(item['Transfer Delay'] for item in latency))
    results['mean_transfer_delay'] = np.mean(list(item['Transfer Delay'] for item in latency))
    return results


def get_final_batch_throughput(simulator):
    """Function to compute the mean throughput of a simulation in the final batch.

    Parameters
    ----------
    simulator : BaseSimulator
        The simulator used.

    Returns
    -------
    mean_throughput : float
        The mean throughput.

    Raises
    ------
    NotImplementedError
        Raised when convergence mode is disabled for the simulator.
    """
    # Check if convergence mode is enabled
    if not simulator.convergence:
        raise NotImplementedError("Final batch throughput calculation is only applicable for convergence mode.")
    # Extract statistics of final batch
    stats = simulator.batch_stats[-1]
    start = stats['start_index']
    end = stats['end_index']
    latency_batch = simulator.latency[start:end]
    mean_throughput = _get_mean_throughput(simulator=simulator, latency=latency_batch)
    return mean_throughput


def get_extended_run_throughput(simulator):
    """Function to compute the mean throughput of a simulation during the extended run.

    Parameters
    ----------
    simulator : BaseSimulator
        The simulator used.

    Returns
    -------
    mean_throughput : float
        The mean throughput.

    Raises
    ------
    NotImplementedError
        Raised when convergence mode is disabled for the simulator.
    ValueError
        Raised when extended run is disabled for the simulator.
    """
    # Check if convergence mode is enabled
    if not simulator.convergence:
        raise NotImplementedError("Extended run throughput calculation is only applicable for convergence mode.")
    # Check if extended run is enabled
    elif not simulator.extended:
        raise ValueError("Extended run is disabled for the simulator.")
    start = simulator.batch_stats[-1]['end_index']
    latency_batch = simulator.latency[start:]
    mean_throughput = _get_mean_throughput(simulator=simulator, latency=latency_batch)
    return mean_throughput


def get_overall_throughput(simulator):
    """Function to compute the overall mean throughput of a simulation.

    Parameters
    ----------
    simulator : BaseSimulator
        The simulator used.

    Returns
    -------
    mean_throughput : float
        The mean throughput.
    """
    mean_throughput = _get_mean_throughput(simulator=simulator, latency=simulator.latency)
    return mean_throughput


def _get_mean_throughput(simulator, latency):
    """Function to compute the mean throughput of a given latency batch.

    Parameters
    ----------
    simulator : BaseSimulator
        The simulator used.
    latency : list
        The list of latency information.

    Returns
    -------
    mean_throughput : float
        The mean throughput of the given latency batch.
    """
    interval = latency[-1]['Latency Timestamp'] - latency[0]['Latency Timestamp']
    mean_throughput = len(latency) * simulator.model.data_signal.size * 8 / interval
    return mean_throughput
