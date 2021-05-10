__all__ = ["BaseTransmitter"]
__author__ = ["Hongyi Yang"]

from NetworkSim.architecture.setup.model import Model
from NetworkSim.simulation.tools.clock import TransmitterDataClock, ControlClock, ReceiverDataClock


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
    simulator : BaseSimulator
        The simulator used.
    model : Model, optional
        The network model used for the simulation.
        Default is ``Model()``.

    Attributes
    ----------
    transmitted_data_packet : list
        A list keeping the information of the transmitted data packets, containing the columns:

        - `Timestamp`
        - `Raw Packet`
        - `Destination ID`
    transmitted_control_packet : list
        A list keeping the information of the transmitted control packets, containing the columns:

        - `Timestamp`
        - `Raw Packet`
        - `Destination ID`
    """

    def __init__(
            self,
            env,
            ram,
            transmitter_id,
            simulator,
            until,
            model=None
    ):
        self.env = env
        self.ram = ram
        self.transmitter_id = transmitter_id
        self.simulator = simulator
        self.until = until
        if model is None:
            model = Model()
        self.model = model
        self._transmitter_data_clock_cycle = TransmitterDataClock(model=model).clock_cycle
        self._receiver_data_clock_cycle = ReceiverDataClock(model=model).clock_cycle
        self._control_clock_cycle = ControlClock(model=model).clock_cycle
        self.transmitted_data_packet = []
        self.transmitted_control_packet = []
        self._tunable_keywords = {'tunable', 't', 'T'}

    def get_packet_from_ram(self, is_upstream=False):
        """
        Get first packet from RAM queue.

        Parameters
        ----------
        is_upstream : bool, optional
            If the packet is in upstream queue. Default is ``False``. \
                This is used only for bi-directional systems.

        Returns
        -------
        generation_timestamp : float
            Time of packet generation.
        data_packet : str
            Data packet to be transmitted.
        destination_id : int
            The ID of the destination node.
        """
        if self.simulator.bidirectional:
            if is_upstream:
                generation_timestamp, data_packet, destination_id = self.ram.upstream_queue.popleft()
            else:
                generation_timestamp, data_packet, destination_id = self.ram.downstream_queue.popleft()
        else:
            generation_timestamp, data_packet, destination_id = self.ram.queue.popleft()
        self.ram.record_queue_size()
        self.ram.pop_from_queue_record.append([generation_timestamp, data_packet, destination_id])
        self.simulator.ram_queue_delay.append(self.env.now - generation_timestamp)
        return generation_timestamp, data_packet, destination_id

    def transmit_control_packet(self, packet, destination_id, generation_timestamp):
        """
        Control packet transmission function.

        This function adds the control packet onto the ring and keeps a record of the transmission.

        Parameters
        ----------
        packet : packet
            The control packet.
        destination_id : int
            The ID of the node to which the control packet is transmitted.
        generation_timestamp : float
            The timestamp when the control packet is generated and stored in RAM.
        """
        # Add control packet onto the ring
        self.model.control_ring.add_packet(
            packet=packet,
            generation_timestamp=generation_timestamp,
            transmission_timestamp=self.env.now,
            node_id=self.transmitter_id,
            destination_id=destination_id
        )
        # Store control packet information
        self.transmitted_control_packet.append([
            self.env.now,
            packet,
            destination_id
        ])

    def transmit_data_packet(self, ring_id, packet, destination_id, generation_timestamp, reversed=False):
        """
        Data packet transmission function.

        This function adds the data packet onto the ring and keeps a record of the transmission.

        Parameters
        ----------
        ring_id : int
            The ID of the data ring on which the packet is transmitted.
        packet : packet
            The data packet.
        destination_id : int
            The ID of the node to which the data packet is transmitted.
        generation_timestamp : float
            The timestamp when the data packet is generated and stored in RAM.
        reversed : bool, optional
            If checking the reversed ring. Defaults is ``False``.
        """
        # Add data packet onto the ring
        if reversed:
            self.model.reversed_data_rings[ring_id].add_packet(
                packet=packet,
                generation_timestamp=generation_timestamp,
                transmission_timestamp=self.env.now,
                node_id=self.transmitter_id,
                destination_id=destination_id
            )
        else:
            self.model.data_rings[ring_id].add_packet(
                packet=packet,
                generation_timestamp=generation_timestamp,
                transmission_timestamp=self.env.now,
                node_id=self.transmitter_id,
                destination_id=destination_id
            )
        # Store data packet information
        self.transmitted_data_packet.append([
            self.env.now,
            packet,
            destination_id
        ])

    def ring_is_full(self, ring_id, reversed=False):
        """
        Function to check if the data ring is fully occupied.

        Parameters
        ----------
        ring_id : int
            The ID of the data ring on which the packet is transmitted.
        reversed : bool, optional
            If checking the reversed ring. Defaults is ``False``.

        Returns
        -------
        ring_is_full : bool
            ``True`` if the data ring is full, otherwise ``False``.
        """
        if self.simulator.bidirectional:
            if reversed:
                if self.model.reversed_data_rings[ring_id].packet_count == self.model.max_data_packet_num_on_ring:
                    return True
                else:
                    return False
        if self.model.data_rings[ring_id].packet_count == self.model.max_data_packet_num_on_ring:
            return True
        return False

    def check_data_packet(self, ring_id, reversed=False):
        """
        Function to check if there is a data packet present at the transmitter

        Parameters
        ----------
        ring_id : int
            The ID of the data ring on which the packet is transmitted.
        reversed : bool, optional
            If checking the reversed ring. Defaults is ``False``.

        Returns
        -------
        present : bool
            Presence of the data packet. ``True`` if present, ``False`` if not present.
        packet : packet
            Packet information, in the format:

            - `raw_packet`
            - `generation_timestamp`
            - `transmission_timestamp`
            - `packet_entry_point`
            - `entry_node_id`
            - `destination_node_id`
        """
        if reversed:
            return self.model.reversed_data_rings[ring_id].check_packet(
                current_time=self.env.now,
                node_id=self.transmitter_id
            )
        else:
            return self.model.data_rings[ring_id].check_packet(
                current_time=self.env.now,
                node_id=self.transmitter_id
            )

    def check_data_packet_after_guard_interval(self, ring_id):
        """
        Function to check if there is a data packet present at the transmitter after the guard interval

        Returns
        -------
        present : bool
            Presence of the data packet. ``True`` if present, ``False`` if not present.
        packet : packet
            Packet information, in the format:

            - `raw_packet`
            - `generation_timestamp`
            - `transmission_timestamp`
            - `packet_entry_point`
            - `entry_node_id`
            - `destination_node_id`
        """
        return self.model.data_rings[ring_id].check_packet(
            current_time=self.env.now + self.model.constants.get('data_guard_interval'),
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
            - `generation_timestamp`
            - `transmission_timestamp`
            - `packet_entry_point`
            - `entry_node_id`
            - `destination_node_id`
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
            control_code=control
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
        """
        if self.simulator.receiver_type in self._tunable_keywords:
            self.env.process(self.transmit_on_control_ring())
        self.env.process(self.transmit_on_data_ring())
