__all__ = ["BaseReceiver"]
__author__ = ["Hongyi Yang"]

from collections import deque

from NetworkSim.architecture.setup.model import Model
from NetworkSim.simulation.tools.clock import TransmitterDataClock, ControlClock, ReceiverDataClock


class BaseReceiver:
    """
    Receiver processes creator for the simulation.

    Parameters
    ----------
    env : simpy Environment
        The simulation environment.
    until : float
        The end time of the simulation.
    receiver_id : int
        The receiver ID.
    simulator : BaseSimulator
        The simulator used.
    model : Model, optional
        The network model used for the simulation.
        Default is ``Model()``.

    Attributes
    ----------
    received_data_packet : list
        A list keeping the information of the received data packets, containing the columns:

        - `Timestamp`
        - `Raw Packet`
        - `Source ID`
    received_control_packet : list
        A list keeping the information of the received control packets, containing the columns:

        - `Timestamp`
        - `Raw Packet`
        - `Source ID`
    queue_record : list
        A list keeping the information of the control packets stored in the receiver RAM, including the columns:

        - `Timestamp` : float
            The timestamp when the operation is carried out.
        - `Raw Packet` : str
            The raw control packet.
        - `Source ID` : int
            Source ID of the control packet.
        - `Operation` : str
            Operation carried out on the packet in the queue.
    queue : list
        A list of packet in the receiver RAM queue, in the format:

        - `raw_packet`
        - `generation_timestamp`
        - `transmission_timestamp`
        - `packet_entry_point`
        - `entry_node_id`
        - `destination_node_id`
        - `reception_timestamp`
    """

    def __init__(
            self,
            env,
            until,
            receiver_id,
            simulator,
            model=None
    ):
        self.env = env
        self.until = until
        self.receiver_id = receiver_id
        self.simulator = simulator
        if model is None:
            model = Model()
        self.model = model
        self._transmitter_data_clock_cycle = TransmitterDataClock(model=model).clock_cycle
        self._receiver_data_clock_cycle = ReceiverDataClock(model=model).clock_cycle
        self._control_clock_cycle = ControlClock(model=model).clock_cycle
        self.received_data_packet = []
        self.received_control_packet = []
        self.queue_record = []
        self.queue = deque()
        self._fixed_keywords = {'fixed', 'f', 'F'}
        self._tunable_keywords = {'tunable', 't', 'T'}
        if self.simulator.receiver_type in self._tunable_keywords:
            self._time_compensation = self._receiver_data_clock_cycle - \
                (self.model.data_packet_duration % self._receiver_data_clock_cycle)
        else:
            self._time_compensation = self._transmitter_data_clock_cycle - self.model.data_packet_duration

    def is_upstream(self, source_id):
        """
        Check if the destination node is an upstream node.

        Parameters
        ----------
        source_id : int
            ID of the source node.

        Returns
        -------
        is_upstream : bool
            ``True`` if the destination is upstream, ``False`` if downstream.
        """
        _difference = self.receiver_id - source_id
        if _difference < 0:
            _difference += self.model.network.num_nodes
        if _difference <= self.model.network.num_nodes / 2:
            return False
        else:
            return True

    def record_error(self, packet, reversed=False):
        """
        Check packet information and record error of data packet transmission.

        Parameters
        ----------
        packet : packet
            The data packet
        reversed : bool, optional
            If the receiver is receiving on the reversed data rings.
        """
        if packet[5] != self.receiver_id:
            error_type = 'destination ID mismatch'
            self.simulator.error.append([
                self.env.now,
                packet[4],
                packet[5],
                error_type
            ])
        # Check if packet circulates around the ring in TT-FR configuration
        if self.simulator.receiver_type in self._fixed_keywords \
                and self.env.now - packet[2] > self.model.circulation_time:
            error_type = 'circulation for TT-FR'
            self.simulator.error.append([
                self.env.now,
                packet[4],
                packet[5],
                error_type
            ])
        # Check if packet is sent on the correct direction for bidirectional systems
        if self.simulator.bidirectional:
            if reversed:
                if not self.is_upstream(source_id=packet[4]):
                    error_type = 'downstream data found on upstream'
                    self.simulator.error.append([
                        self.env.now,
                        packet[4],
                        packet[5],
                        error_type
                    ])
            else:
                if self.is_upstream(source_id=packet[4]):
                    error_type = 'upstream data found on downstream'
                    self.simulator.error.append([
                        self.env.now,
                        packet[4],
                        packet[5],
                        error_type
                    ])

    def record_latency(self, packet):
        """
        Record latency of the data packet transmission.

        Parameters
        ----------
        packet : packet
            The control packet.
        """
        data_rate = (len(self.simulator.latency) + 1) * self.model.data_signal.size * 8 / self.env.now
        self.simulator.latency.append({
            'Latency Timestamp': self.env.now,
            'Source ID': packet[4],  # Source node
            'Destination ID': packet[5],  # Destination node
            'Queueing Delay': packet[2] - packet[1],  # Queueing delay
            'Transfer Delay': self.env.now - packet[1],  # Transfer delay
            'Data Rate': data_rate
        })

    def control_id_match(self, packet):
        """
        Function to check if the control packet destination ID matches the receiver ID.

        Parameters
        ----------
        packet : packet
            The control packet.

        Returns
        -------
        if_match : bool
            If the received packet ID matches that of the receiver. ``True`` if matched, otherwise ``False``.
        """
        # Interpret control packet
        source_id, destination_id, control_code = self.interpret_control_packet(packet)
        if destination_id == self.receiver_id:
            return True
        return False

    def get_original_control_packet(self, packet):
        """
        Locate the original control packet if a new control packet with "Remove" code is obtained.

        Parameters
        ----------
        packet : packet
            The control packet.

        Returns
        -------
        original_packet : packet
            The original control packet if found. Otherwise return ``None``.
        """
        # Interpret latest control packet information
        source_id, destination_id, control_code = self.interpret_control_packet(packet)
        # Generate original control packet by changing the control code
        control = 0  # Original "Add" control code
        raw_control_packet = self.model.control_signal.generate_packet(
            source=source_id,
            destination=destination_id,
            control_code=control
        )
        # Return the control packet in receiver RAM queue with the same raw packet and correct circulation time
        _circulation_time = self.model.network.length / self.model.constants.get('speed')
        for packet in self.queue:
            time_difference = self.env.now - packet[6]
            if packet[0] == raw_control_packet and not (time_difference % _circulation_time):
                return packet
        return None

    def ram_queue_input(self, packet, priority='low'):
        """
        Handling input to the receiver RAM queue.

        Parameters
        ----------
        packet : packet
            The control packet.
        priority : str
            Priority of the packet:

            - If `"high"`, the packet is inserted to the list (at the beginning). \
            - If `"low"`, the packet is append to the list (at the end).

            Default is ``"low"``.
        """
        # Interpret control packet information and store its information
        source_id, destination_id, control_code = self.interpret_control_packet(packet)
        # Determine and perform control packet operation
        if not control_code:  # Packet added
            operation = "Added"
            packet.append(self.env.now)
            if priority == 'high':
                self.queue.appendleft(packet)
            else:
                self.queue.append(packet)
        elif control_code == 1:  # Previously added packet now removed
            operation = "Removed"
            original_packet = self.get_original_control_packet(packet=packet)
            self.queue.remove(original_packet)
        else:
            operation = "Unknown"
        # Record RAM queue information
        self.queue_record.append([
            self.env.now,
            packet[0],
            packet[4],
            operation
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
            reception_timestamp=self.env.now
        )
        # Store control packet information
        self.received_control_packet.append([
            self.env.now,
            packet[0],
            packet[4]
        ])

    def ram_queue_output(self, packet):
        """
        Handling output from the receiver RAM queue.

        Parameters
        ----------
        packet : packet
            The control packet read from the front of the queue.

        Returns
        -------
        source_id : int
            The data ring to tune to for reception.
        """
        # Interpret control packet information and store its information
        source_id, destination_id, control_code = self.interpret_control_packet(packet)
        # Record RAM queue information
        operation = "Processed"
        self.queue_record.append([
            self.env.now,
            packet[0],
            packet[4],
            operation
        ])
        # Return the receiving ring to tune to
        return source_id

    def receive_data_packet(self, ring_id, packet, reversed=False):
        """
        Data packet reception function.

        This function removes the data packet from the ring and keeps a record of the transmission.

        Parameters
        ----------
        ring_id : int
            The ID of the data ring where the packet is removed.
        packet : packet
            The data packet.
        reversed : bool, optional
            If the receiver is receiving on the reversed data rings.
        """
        if reversed:
            # Remove data packet from the ring
            # packet contains [raw_packet, timestamp, entry_point, source_node_id]
            self.model.reversed_data_rings[ring_id].remove_packet(
                node_id=self.receiver_id,
                packet=packet,
                reception_timestamp=self.env.now
            )

        else:
            self.model.data_rings[ring_id].remove_packet(
                node_id=self.receiver_id,
                packet=packet,
                reception_timestamp=self.env.now
            )
        # Store data packet information
        self.received_data_packet.append([
            self.env.now,
            packet[0],
            packet[4]
        ])

    def check_data_packet(self, ring_id, reversed=False):
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
            - `generation_timestamp`
            - `transmission_timestamp`
            - `packet_entry_point`
            - `entry_node_id`
            - `destination_node_id`
        """
        if reversed:
            return self.model.reversed_data_rings[ring_id].check_packet(
                current_time=self.env.now,
                node_id=self.receiver_id
            )
        else:
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
            - `generation_timestamp`
            - `transmission_timestamp`
            - `packet_entry_point`
            - `entry_node_id`
            - `destination_node_id`
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
            - `generation_timestamp`
            - `transmission_timestamp`
            - `packet_entry_point`
            - `entry_node_id`
            - `destination_node_id`

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
        if self.simulator.receiver_type in self._tunable_keywords:
            self.env.process(self.receive_on_control_ring())
        self.env.process(self.receive_on_data_ring())
