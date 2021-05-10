__all__ = ["Model"]
__author__ = ["Hongyi Yang"]

import numpy as np

from NetworkSim.architecture.base.network import Network
from NetworkSim.architecture.base.node import Node
from NetworkSim.architecture.base.ring import Ring
from NetworkSim.architecture.signal.control import ControlSignal
from NetworkSim.architecture.signal.data import DataSignal


class Model:
    """
    Constructor for model.

    The model includes network, node and signal definitions.

    Parameters
    ----------
    control_signal : ControlSignal, optional
        The control signal definition. Default is ``ControlSignal()``.
    data_signal : DataSignal, optional
        The data signal definition. Default is ``DataSignal()``.
    network : Network, optional
        The network definition. Default is ``Network()``.
    abstract : bool
        Abstract representation of control and data packets. Default is ``True``.
    bidirectional : bool, optional
        The type of network architecture, either bidirectional or unidirectional. \
            Default is ``False``, which is unidirectional.


    Attributes
    ----------
    nodes : list
        A list containing the nodes in the model
    data_rings : list
        A list containing the data rings in the model
    control_ring : Ring
        The control ring in the network. The `ring_id` of this ring is ``-1``.
    constants : dict
        A dictionary containing:

        - `speed` : speed of light in the fibre, in m/s
        - `maximum_bit_rate` : maximum bit rate of each channel, in Gbit/s
        - `average_bit_rate` : average bit rate of each channel, in Gbit/s
        - `data_guard_interval` : guard interval of data packets, in ns
        - `control_guard_interval` : guard interval of control packets, in ns
        - `tuning_time` : tuning time of the receiver, in ns
    data_packet_duration : float
        The total duration of the data packet, including the guard interval.
    circulation_time : float
        The time for one complete circulation around the ring.
    max_data_packet_num_on_ring : int
        The maximum number of data packets a ring can contain.
    """

    def __init__(
            self,
            control_signal=None,
            data_signal=None,
            network=None,
            abstract=True,
            bidirectional=False
    ):
        if control_signal is None:
            control_signal = ControlSignal(abstract=abstract)
        self.control_signal = control_signal
        if data_signal is None:
            data_signal = DataSignal(abstract=abstract)
        self.data_signal = data_signal
        if network is None:
            network = Network()
        self.network = network
        self.abstract = abstract
        self.bidirectional = bidirectional
        self.nodes = self.generate_nodes()
        self.data_rings = self.generate_data_rings()
        if self.bidirectional:
            self.reversed_data_rings = self.generate_reversed_data_rings()
        self.control_ring = self.generate_control_ring()
        self.constants = {
            'speed': 2e8,  # speed of light in fibre, in m/s
            'maximum_bit_rate': 100,  # system burst rate (maximum bit rate), in Gbit/s
            'average_bit_rate': 30,  # system average bit rate, in Gbit/s
            'data_guard_interval': 20,  # guard interval of data packets in ns
            'control_guard_interval': 0.14,  # guard interval of control packets in ns
            'tuning_time': 20  # tuning time of the receiver in ns
        }
        self.data_packet_duration = self.get_data_packet_total_duration()
        self.circulation_time = self.get_circulation_time()
        self.max_data_packet_num_on_ring = self.get_max_data_packet_num_on_ring()

    def get_circulation_time(self):
        """
        Calculate time for a signal to circulate around the ring once.

        Returns
        -------
        circulation_time : float
            The time taken for one circulation, in ns.
        """
        return self.network.length / self.constants.get('speed') * 1e9

    def get_data_packet_duration(self):
        """
        Calculation of the duration of a data packet excluding guard interval

        Returns
        -------
        packet_duration : float
            Duration of the data packet, in ns
        """
        # Calculate total time taken by one packet excluding guard interval
        _bit_duration = 1 / self.constants.get('maximum_bit_rate')
        packet_duration = _bit_duration * self.data_signal.size * 8
        return packet_duration

    def get_data_packet_total_duration(self):
        """
        Calculation of the duration of a data packet including guard interval

        Returns
        -------
        total_duration : float
            Duration of the data packet with guard interval, in ns
        """
        # Calculate total time taken by one packet including guard interval
        _bit_duration = 1 / self.constants.get('maximum_bit_rate')
        _packet_duration = _bit_duration * self.data_signal.size * 8
        total_duration = _packet_duration + self.constants.get('data_guard_interval')
        return total_duration

    def get_max_data_packet_num_on_ring(self):
        """
        Obtain the maximum number of data packets that can be fitted in the ring.

        Returns
        -------
        max_packet_num : int
            The maximum number of packets allowed.
        """
        # Calculate total time taken by one packet including guard interval
        _total_duration = self.get_data_packet_total_duration()
        # Calculate total length of one transmission
        _transmission_length = _total_duration * self.constants.get('speed') * 1e-9
        # Calculate maximum number of packets that could be fitted on the ring
        max_packet_num = self.network.length // np.round(_transmission_length, decimals=2)
        # Type cast at the end to avoid TypeError: 'numpy.float64' object cannot be interpreted as an integer
        return max_packet_num

    def get_max_control_packet_num_on_ring(self):
        """
        Obtain the maximum number of control packets that can be fitted in the ring.

        Returns
        -------
        max_packet_num : int
            The maximum number of packets allowed.
        """
        return self.get_max_control_packet_num_between_nodes() * self.network.num_nodes

    def get_max_control_packet_num_between_nodes(self):
        """
        Obtain the maximum number of control packets that can be fitted between two nodes.

        Returns
        -------
        max_packet_num_between_node : int
            The maximum number of packets allowed between two nodes.
        """
        # Calculate total time taken by one packet including guard interval
        _bit_duration = 1 / self.constants.get('maximum_bit_rate')
        _packet_duration = _bit_duration * (2 * self.control_signal.id_length + self.control_signal.control_length)
        _total_duration = _packet_duration + self.constants.get('control_guard_interval')
        # Calculate total length of one transmission
        _transmission_length = _total_duration * self.constants.get('speed') * 1e-9
        # Calculate the distance between two node
        _node_interval = self.network.get_interval()
        if _node_interval < _transmission_length:
            raise ValueError("This configuration would result in control packet larger than the node interval.")
        # Calculate maximum number of packets that could be fitted between two node
        max_packet_num_between_node = _node_interval // np.round(_transmission_length, decimals=2)
        # Type cast at the end to avoid TypeError: 'numpy.float64' object cannot be interpreted as an integer
        return max_packet_num_between_node

    def generate_nodes(self):
        """
        Generate a list of nodes based on the network configuration.

        Returns
        -------
        nodes : list
            List of `Node` objects.
        """
        return [Node(
            control_signal=self.control_signal,
            data_signal=self.data_signal,
            network=self.network,
            node_id=i
        ) for i in range(self.network.num_nodes)]

    def generate_data_rings(self):
        """
        Generate a list of data rings based on the network configuration.

        Returns
        -------
        data_rings : list
            List of `Ring` objects.
        """
        return [Ring(model=self, ring_id=i) for i in range(self.network.num_nodes)]

    def generate_reversed_data_rings(self):
        """
        Generate a list of data rings in the reversed transmission direction based on the network configuration.

        Returns
        -------
        data_rings : list
            List of `Ring` objects with `reversed=True`.
        """
        return [Ring(model=self, ring_id=i, reversed=True) for i in range(self.network.num_nodes)]

    def generate_control_ring(self):
        """
        Generate a control ring based on the network configuration.

        Returns
        -------
        control_ring : Ring
            List of `Ring` objects.
        """
        return Ring(model=self, ring_id=-1)
