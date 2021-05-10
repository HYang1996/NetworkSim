__all__ = ["TR"]
__author__ = ["Hongyi Yang"]

import numpy as np

from NetworkSim.simulation.process.receiver.base import BaseReceiver


class TR(BaseReceiver):
    """
    Tunable receiver simulator.

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
            until,
            receiver_id,
            simulator,
            model=None
    ):
        super().__init__(
            env=env,
            until=until,
            receiver_id=receiver_id,
            simulator=simulator,
            model=model
        )
        self.data_packet_received = True

    def receive_on_control_ring(self):
        """
        Receiver process to remove a new control packet from the ring.

        This process operates at the control clock frequency, and the control packet would only be removed from the \
        ring if the destination ID of the packet corresponds to the receiver ID. The receiver would also check \
        if the data packets reception precess is ready before receiving control packets.

        In this process:

        1. The receiver starts detecting for incoming control packets;
        2. The receiver checks the destination ID of the control packet received;
        3. When the IDs match, the receiver removes the control packet from the ring, keeps a record of the \
        transmission. and informs the data reception subsystem.
        4. Depends on the control_code, the packet will be added to a queue or remove a packet from the queue;
        """
        while self.env.now <= self.until:
            present, packet = self.check_control_packet()
            # Check if a control packet is detected
            if present:
                # Check if control packet destination ID matches own ID
                if self.control_id_match(packet=packet):
                    # Add received control packet into queue
                    self.ram_queue_input(packet=packet)
                    # Remove packet from the ring, keep a record of its information
                    self.receive_control_packet(packet=packet)
            yield self.env.timeout(self._receiver_data_clock_cycle)

    def receive_on_data_ring(self):
        """
        Receiver process to remove a new data packet from the ring.

        This process operates at the unit clock frequency, and the data packet would only be from the \
        ring once its corresponding control packet has been received.

        In this process:

        1. The receiver takes ``'tuning_time'`` to tune to the data ring;
        2. The receiver waits and receives the data packet, \
        removes it from the ring and keeps a record of the transmission.
        3. The latency of the transmission is recorded.
        """
        while self.env.now <= self.until:
            if self.queue:
                # Assign flag
                self.data_packet_received = False
                # Obtain the first control packet in RAM queue
                _control_packet = self.queue.popleft()
                # Tune to incoming data packet wavelength
                _transmitter_id = self.ram_queue_output(_control_packet)
                # Wait for the data packet
                while not self.data_packet_received:
                    # Receive data packet
                    _present, _packet = self.check_data_packet(ring_id=_transmitter_id)
                    _time_difference = self.env.now - _control_packet[6]
                    # Check if a data packet is received and time is correct
                    if _present and \
                            (np.isclose(_time_difference % self.model.circulation_time, 0, atol=1e-2) or
                             np.isclose(_time_difference % self.model.circulation_time,
                                        self.model.circulation_time, atol=1e-2)):
                        # Remove packet from the ring and keep a record of its information
                        self.record_error(_packet)
                        self.receive_data_packet(ring_id=_transmitter_id, packet=_packet)
                        # Wait for the end of the data packet
                        yield self.env.timeout(self.model.data_packet_duration)
                        # Record latency information
                        self.record_latency(packet=_packet)
                        # Assign flag
                        self.data_packet_received = True
                        # Sync with clock
                        yield self.env.timeout(self._time_compensation)
                    else:
                        yield self.env.timeout(self._receiver_data_clock_cycle)
            else:
                yield self.env.timeout(self._receiver_data_clock_cycle)
