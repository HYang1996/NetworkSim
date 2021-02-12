__all__ = ["Node"]
__author__ = ["Hongyi Yang"]

import pandas as pd

from NetworkSim.architecture.base.network import Network
from NetworkSim.architecture.signal.control import ControlSignal
from NetworkSim.architecture.signal.data import DataSignal


class Node:
    """
    Constructor of the individual node in the ring network

    Parameters
    ----------
    node_id : int
        The ID number of the Node. Default is ``None``.
    control_signal : ControlSignal
        The control signal defined in the network.
    data_signal : DataSignal
        The data signal defined in the network.

    Attributes
    ----------
    generated_control_packet_df : pandas DataFrame
        A DataFrame keeping a record of the generated control packets, containing the columns:

        - `Timestamp`
        - `Raw Packet`
        - `Source ID`
        - `Destination ID`
        - `Control Code`
    received_control_packet_df : pandas DataFrame
        A DataFrame keeping a record of the received control packets, containing the columns:

        - `Timestamp`
        - `Raw Packet`
        - `Source ID`
        - `Destination ID`
        - `Control Code`
    generated_data_packet_df : pandas DataFrame
        A DataFrame keeping a record of the generated data packets, containing the columns:

        - `Timestamp`
        - `Raw Packet`
        - `Source ID`
    received_data_packet_df : pandas DataFrame
        A DataFrame keeping a record of the received data packets, containing the columns:

        - `Timestamp`
        - `Raw Packet`
        - `Source ID`
    """

    def __init__(
            self,
            control_signal,
            data_signal,
            network,
            node_id=None
    ):
        # Check input types
        if not isinstance(control_signal, ControlSignal) or \
                not isinstance(data_signal, DataSignal) or \
                not isinstance(network, Network):
            raise ValueError('control_signal must be a ControlSignal object, '
                             'data_signal must be a DataSignal object, '
                             'and network must be a Network object.')
        self.node_id = node_id
        self.control_signal = control_signal
        self.data_signal = data_signal
        self.network = network
        self.generated_control_packet = []
        self.received_control_packet = []
        self.generated_data_packet = []
        self.received_data_packet = []

    def interpret_control_packet(self, packet):
        """
        Interpretation of a control packet.

        Parameters
        ----------
        packet

        Returns
        -------
        source_id : int
            Source ID of the control packet.
        destination_id : int
            Destination iD of the control packet.
        control_code : int
            Control code in decimal.
        """
        # Check type and length of the incoming packet
        if self.control_signal.abstract:
            if not isinstance(packet, list):
                raise ValueError('Abstract signal must be a list.')
        else:
            if not isinstance(packet, str):
                raise ValueError('Signal input must be a string.')
        # Control packet interpretation
        if self.control_signal.abstract:
            return packet[0], packet[1], packet[2]
        else:
            _total_length = 2 * self.control_signal.id_length + self.control_signal.control_length
            if len(packet) != _total_length:
                raise ValueError(f'Signal bit length is incorrect, expecting {_total_length} bits.')
            # Separate signal into 3 parts
            _packet_source = packet[0:self.control_signal.id_length]
            _packet_destination = packet[self.control_signal.id_length: 2 * self.control_signal.id_length]
            _packet_code = packet[2 * self.control_signal.id_length:]
            source_id = int(_packet_source, 2)
            destination_id = int(_packet_destination, 2)
            control_code = int(_packet_code, 2)
            return source_id, destination_id, control_code

    def generate_control_packet(self, destination_id, control_code, timestamp):
        """
        Control packet generation.

        Parameters
        ----------
        destination_id : int
            The node ID of the destination node.
        control_code : int
            The control code in decimal.
        timestamp : float
            The timestamp when the control packet is generated.

        Returns
        -------
        control_packet : str
            A string representation of the control packet in binary.
        """
        # Check input type
        if not isinstance(destination_id, int):
            raise ValueError('Destination node ID must be an integer.')
        control_packet = self.control_signal.generate_packet(
            source=self.node_id,
            destination=destination_id,
            control_code=control_code
        )
        self.generated_control_packet.append([
            timestamp,
            control_packet,
            self.node_id,
            destination_id,
            control_code
        ])
        return control_packet

    def store_received_control_packet(self, packet, timestamp):
        """
        Storage of received control packets.
        The packets are interpreted and stored in `self.received_control_packet_df`.

        Parameters
        ----------
        packet : str
            Received control packet string in binary.
        timestamp : float
            The timestamp when the control packet is received.
        """
        # Check type and length of the incoming packet
        if self.control_signal.abstract:
            if not isinstance(packet, list):
                raise ValueError('Abstract control packet must be a list.')
        else:
            if not isinstance(packet, str):
                raise ValueError('Signal input must be a string')
            total_length = 2 * self.control_signal.id_length + self.control_signal.control_length
            if len(packet) != total_length:
                raise ValueError(f'Signal bit length is incorrect, expecting {total_length} bits.')
        source_id, destination_id, control_code = self.interpret_control_packet(packet=packet)
        self.received_control_packet.append([
            timestamp,
            packet,
            source_id,
            destination_id,
            control_code
        ])

    def generate_data_packet(self, destination_id, timestamp):
        """
        Data packet generation.

        Parameters
        ----------
        destination_id : int
            The node ID of the destination node.
        timestamp : float
            The timestamp when the data packet is generated.

        Returns
        -------
        data_packet : str
            The data packet string in binary.
        """
        # Check input type
        if not isinstance(destination_id, int):
            raise ValueError('Destination node ID must be an integer.')
        data_packet = self.data_signal.generate_packet()
        self.generated_data_packet.append([
            timestamp,
            data_packet,
            destination_id
        ])
        return data_packet

    def store_received_data_packet(self, packet, source_id, timestamp):
        """
        Storage of received data packet.
        The data packet is stored in `self.received_data_packet_df`.

        Parameters
        ----------
        packet : str
            The received data packet string in binary.
        source_id : int
            The node ID of the source node.
        timestamp
            The timestamp when the data packet is received.
        """
        # Check type and length of the incoming packet
        if not self.data_signal.abstract:
            if not isinstance(packet, str):
                raise ValueError('Signal input must be a string')
            if len(packet) != 8 * self.data_signal.size:
                raise ValueError(f'Signal bit length is incorrect, expecting {8 * self.data_signal.size} bits.')
        if not isinstance(source_id, int):
            raise ValueError('Source node ID must be an integer.')
        self.received_data_packet.append([
            timestamp,
            packet,
            source_id
        ])

    def get_distance_to(self, end_node):
        """
        Get distance to a node.

        Parameters
        ----------
        end_node : Node
            The end node.

        Returns
        -------
        distance : float
            The distance from current node to the end node in meters.

        """
        # Check input type
        if not isinstance(end_node, Node):
            raise ValueError('End node must be a Node object.')
        return self.network.get_distance(self.node_id, end_node.node_id)

    def get_distance_from(self, start_node):
        """
        Get distance from a node.

        Parameters
        ----------
        start_node : Node
            The start node.

        Returns
        -------
        distance : float
            The distance from the start node to the current node in meters.
        """
        # Check input type
        if not isinstance(start_node, Node):
            raise ValueError('Start node must be a Node object.')
        return self.network.get_distance(start_node.node_id, self.node_id)

    def summary(self):
        """
        Obtain a summary of the node.

        Returns
        -------
        summary : pandas DataFrame
            A summary of the Node, containing the columns:

            - `Node ID`
            - `Control Signal ID (bit)`
            - `Control Signal Code (bit)`
            - `Data Packet Size (byte)`
        """
        summary = {
            'Node ID': self.node_id,
            'Control Signal ID (bit)': [self.control_signal.id_length],
            'Control Signal Code (bit)': [self.control_signal.control_length],
            'Data Packet Size (byte)': [self.data_signal.size]
        }
        return pd.DataFrame(data=summary)
