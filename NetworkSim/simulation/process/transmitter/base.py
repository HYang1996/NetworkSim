__all__ = ["BaseTransmitter"]
__author__ = ["Hongyi Yang"]

import pandas as pd

from NetworkSim.architecture.setup.model import Model
from NetworkSim.simulation.tools.clock import DataClock, ControlClock


class BaseTransmitter:
    """
    Transmitter processes creator for the simulation.

    Parameters
    ----------
    env : simpy Environment
        The simulation environment.
    ram : RAM
        The RAM at which the transmitter access its information.
    transmitter_id : int
        The transmitter ID.
    model : Model, optional
        The network model used for the simulation.
        Default is ``Model()``.

    Attributes
    ----------
    transmitted_data_packet_df : pandas DataFrame
        A DataFrame keeping the information of the transmitted data packets, containing the columns:

        - `Timestamp`
        - `Raw Packet`
        - `Destination ID`
    transmitted_control_packet_df : pandas DataFrame
        A DataFrame keeping the information of the transmitted control packets, containing the columns:

        - `Timestamp`
        - `Raw Packet`
        - `Destination ID`
    """
    def __init__(
            self,
            env,
            ram,
            transmitter_id,
            model=None
    ):
        self.env = env
        self.ram = ram
        self.transmitter_id = transmitter_id
        if model is None:
            model = Model()
        self.model = model
        self.data_clock_cycle = DataClock(model=model).clock_cycle
        self.control_clock_cycle = ControlClock(model=model).clock_cycle
        data = []
        self.transmitted_data_packet_df = pd.DataFrame(data, columns=[
            'Timestamp',
            'Raw Packet',
            'Destination ID'
        ])
        self.transmitted_control_packet_df = pd.DataFrame(data, columns=[
            'Timestamp',
            'Raw Packet',
            'Destination ID'
        ])

    def transmit_control_packet(self, packet, destination_id):
        """
        Control packet transmission function.

        This function adds the control packet onto the ring and keeps a record of the transmission.

        Parameters
        ----------
        packet : packet
            The control packet.
        destination_id : int
            The ID of the node to which the control packet is transmitted.
        """
        # Add control packet onto the ring
        self.model.control_ring.add_packet(
            packet=packet,
            timestamp=self.env.now,
            node_id=self.transmitter_id,
            destination_id=destination_id
        )
        # Store control packet information
        self.transmitted_control_packet_df = self.transmitted_control_packet_df.append({
            'Timestamp': self.env.now,
            'Raw Packet': packet,
            'Destination ID': destination_id
        }, ignore_index=True)

    def transmit_data_packet(self, packet, destination_id):
        """
        Data packet transmission function.

        This function adds the data packet onto the ring and keeps a record of the transmission.

        Parameters
        ----------
        packet : packet
            The data packet.
        destination_id : int
            The ID of the node to which the data packet is transmitted.
        """
        # Add data packet onto the ring
        self.model.data_rings[self.transmitter_id].add_packet(
            packet=packet,
            timestamp=self.env.now,
            node_id=self.transmitter_id,
            destination_id=destination_id
        )
        # Store data packet information
        self.transmitted_data_packet_df = self.transmitted_data_packet_df.append({
            'Timestamp': self.env.now,
            'Raw Packet': packet,
            'Destination ID': destination_id
        }, ignore_index=True)

    def transmit_without_checking(self):
        """
        A dummy transmitter to transmit data packets without checking ring slot availability.
        """
        while True:
            if len(self.ram.queue) != 0:
                # Obtain packet information in the queue
                timestamp, data_packet, destination_id = self.ram.queue.pop(0)
                # Transmit the data packet
                self.transmit_data_packet(
                    packet=data_packet,
                    destination_id=destination_id
                )
            yield self.env.timeout(self.data_clock_cycle)

    def ring_is_full(self):
        """
        Function to check if the data ring is fully occupied.

        Returns
        -------
        ring_is_full : bool
            ``True`` if the data ring is full, otherwise ``False``.
        """
        if self.model.data_rings[self.transmitter_id].packet_count == self.model.get_max_data_packet_num_on_ring():
            return True
        else:
            return False

    def check_data_packet(self):
        """
        Function to check if there is a data packet present at the transmitter

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
        return self.model.data_rings[self.transmitter_id].check_packet(
            current_time=self.env.now,
            node_id=self.transmitter_id
        )

    def check_control_packet(self):
        """
        Function to check if there is a control packet present at the transmitter

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
            node_id=self.transmitter_id
        )

    def generate_control_packet(self, destination, control):
        """
        Function to generate a control packet.

        Returns
        -------
        control_packet : str
            The raw control packet string in binary
        """
        return self.model.control_signal.generate_packet(
            source=self.transmitter_id,
            destination=destination,
            control=control
        )

    def transmit_on_data_ring(self):
        """
        Process to transmit data packets.
        """
        raise NotImplementedError("This is an abstract data packet transmission process method.")

    def transmit_on_control_ring(self):
        """
        Process to transmit control packets.
        """
        raise NotImplementedError("This is an abstract control packet transmission process method.")

    def initialise(self):
        """
        Initialisation of the transmitter simulation.

        This function adds two asynchronous transmitter processes into the environment:

        - Transmission of control packets
        - Transmission of data packets
        """
        self.env.process(self.transmit_on_data_ring())
        self.env.process(self.transmit_on_control_ring())
