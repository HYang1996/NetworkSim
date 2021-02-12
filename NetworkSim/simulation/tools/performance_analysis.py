"""
Utilities for calculating network performance analysis
"""

__all__ = [
    "get_transfer_delay",
    "get_throughput"
]
__author__ = ["Hongyi Yang"]


def get_queueing_delay(simulator):
    """
    Calculate the queueing delay latency of the defined network.

    Parameters
    ----------
    simulator : BaseSimulator
        The simulator used to create the network.

    Returns
    -------
    queueing_delay : float
        The estimated average queueing delay latency of the network.
    """
    t_t = simulator.model.constants.get('tuning_time')
    t_s = simulator.model.circulation_time / simulator.model.max_data_packet_num_on_ring
    N = simulator.model.network.num_nodes
    lambda_a = simulator.model.constants.get('average_bit_rate') / simulator.model.data_signal.size / 8
    W = simulator.model.network.num_nodes
    queueing_delay = t_s / 2 + t_t * (N - 1) / N + (t_s * t_s * N * lambda_a) / (2 * W - t_s * N * lambda_a)
    service_time = queueing_delay + t_s
    mu = 1 / service_time
    rho = lambda_a / mu
    ram_queue_delay = rho / (mu - lambda_a)
    return queueing_delay + ram_queue_delay


def get_transfer_delay(simulator):
    """
    Calculate the transfer delay latency of the defined network.

    Parameters
    ----------
    simulator : BaseSimulator
        The simulator used to create the network.

    Returns
    -------
    transfer_delay : float
        The estimated average transfer delay latency of the network.
    """
    t_tr = simulator.model.data_packet_duration
    t_pd = simulator.model.circulation_time
    transfer_delay = get_queueing_delay(simulator=simulator) + t_tr + t_pd / 2
    return transfer_delay


def get_throughput(simulator):
    raise NotImplementedError("Throughput calculation not implemented.")
