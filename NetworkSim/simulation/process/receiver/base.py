__all__ = ["BaseReceiver"]
__author__ = ["Hongyi Yang"]

import pandas as pd

from NetworkSim.architecture.setup.model import Model
from NetworkSim.simulation.tools.clock import DataClock, ControlClock


class BaseReceiver:
    """
    Receiver processes creator for the simulation.

    Parameters
    ----------
    env : simpy Environment
        The simulation environment.
    receiver_id : int
        The receiver ID.
    model : Model, optional
        The network model used for the simulation.
        Default is ``Model()``.

    Attributes
    ----------
    received_data_packet_df : pandas DataFrame
        A DataFrame keeping the information of the received data packets, containing the columns:

        - `Timestamp`
        - `Raw Packet`
        - `Source ID`
    received_control_packet_df : pandas DataFrame
        A DataFrame keeping the information of the received control packets, containing the columns:

        - `Timestamp`
        - `Raw Packet`
        - `Source ID`
    """
    def __init__(
            self,
            env,
            receiver_id,
            model=None
    ):
        self.env = env
        self.receiver_id = receiver_id
        if model is None:
            model = Model()
        self.model = model
        self.data_clock_cycle = DataClock(model=model).clock_cycle
        self.control_clock_cycle = ControlClock(model=model).clock_cycle
        data = []
        self.received_data_packet_df = pd.DataFrame(data, columns=[
            'Timestamp',
            'Raw Packet',
            'Source ID'
        ])
        self.received_control_packet_df = pd.DataFrame(data, columns=[
            'Timestamp',
            'Raw Packet',
            'Source ID'
        ])

    def receive_control_packet(self, packet):
        """
        Control packet reception function.

        This function removes the control packet from the ring and keeps a record of the transmission.

        Parameters
        ----------
        packet : packet
            The control packet.
        """
        # Remove control packet from the ring
        # packet contains [raw_packet, timestamp, entry_point, source_node_id]
        self.model.control_ring.remove_packet(
            node_id=self.receiver_id,
            packet=packet,
            timestamp=self.env.now
        )
        # Store control packet information
        self.received_control_packet_df = self.received_control_packet_df.append({
            'Timestamp': self.env.now,
            'Raw Packet': packet[0],
            'Source ID': packet[3]
        }, ignore_index=True)

    def receive_data_packet(self, ring_id, packet):
        """
        Data packet reception function.

        This function removes the data packet from the ring and keeps a record of the transmission.

        Parameters
        ----------
        ring_id : int
            The ID of the data ring where the packet is removed.
        packet : packet
            The data packet.
        """
        # Remove data packet from the ring
        # packet contains [raw_packet, timestamp, entry_point, source_node_id]
        self.model.data_rings[ring_id].remove_packet(
            node_id=self.receiver_id,
            packet=packet,
            timestamp=self.env.now
        )
        # Store data packet information
        self.received_data_packet_df = self.received_data_packet_df.append({
            'Timestamp': self.env.now,
            'Raw Packet': packet[0],
            'Source ID': packet[3]
        }, ignore_index=True)

    def check_data_packet(self, ring_id):
        """
        Function to check if there is a data packet present at the receiver

        Parameters
        ----------
        ring_id : int
            The ID of the data ring to check.

        Returns
        -------
        present : bool
            Presence of the data packet. ``True`` if present, ``False`` if not present.
        packet : packet
            Packet information, in the format:

            - `raw_packet`
            - `timestamp`
            - 'packet_entry_point'
            - `entry_node_id`
        """
        return self.model.data_rings[ring_id].check_packet(
            current_time=self.env.now,
            node_id=self.receiver_id
        )

    def check_control_packet(self):
        """
        Function to check if there is a control packet present at the receiver

        Returns
        -------
        present : bool
            Presence of the data packet. ``True`` if present, ``False`` if not present.
        packet : packet
            Packet information, in the format:

            - `raw_packet`
            - `timestamp`
            - 'packet_entry_point'
            - `entry_node_id`
        """
        return self.model.control_ring.check_packet(
            current_time=self.env.now,
            node_id=self.receiver_id
        )

    def interpret_control_packet(self, packet):
        """
        Function to interpret a control packet.

        Parameters
        ----------
        packet : packet
            Packet information, in the format:

            - `raw_packet`
            - `timestamp`
            - 'packet_entry_point'
            - `entry_node_id`

        Returns
        -------
        source_id : int
            The source ID.
        destination_id : int
            The destination ID.
        control_code : int
            The control code.
        """
        return self.model.nodes[self.receiver_id].interpret_control_packet(packet[0])

    def receive_on_control_ring(self):
        """
        Process to receive control packets.
        """
        raise NotImplementedError("This is an abstract control packet reception process method.")

    def receive_on_data_ring(self):
        """
        Process to receive data packets.
        """
        raise NotImplementedError("This is an abstract data packet reception process method.")

    def initialise(self):
        """
        Initialisation of the receiver simulation.

        This function adds two asynchronous receiver processes into the environment:

        - Reception of control packets
        - Reception of data packets
        """
        self.env.process(self.receive_on_control_ring())
        self.env.process(self.receive_on_data_ring())
