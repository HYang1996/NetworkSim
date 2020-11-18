__all__ = ["TR"]
__author__ = ["Hongyi Yang"]

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
            receiver_id,
            model=None
    ):
        super().__init__(
            env=env,
            receiver_id=receiver_id,
            model=model
        )
        self.control_packet_received = False
        self.data_packet_received = True
        self.tune_to_ring = receiver_id
        self.tuned = False

    def receive_on_control_ring(self):
        """
        Receiver process to remove a new control packet from the ring.

        This process operates at the control clock frequency, and the control packet would only be removed from the \
        ring if the destination ID of the packet corresponds to the receiver ID. The receiver would also check \
        if the data packets reception precess is ready before receiving control packets.

        In this process:

        1. The receiver starts detecting for incoming control packets when data reception is ready;
        2. The receiver checks the destination ID of the control packet received;
        3. When the IDs match, the receiver removes the control packet from the ring, keeps a record of the \
        transmission, and informs the data reception subsystem.
        """
        while True:
            # Check if data reception is ready
            if self.data_packet_received:
                present, packet = self.check_control_packet()
                # Check if a control packet is detected
                if present:
                    # Check if control packet destination ID matches own ID
                    source_id, destination_id, control_code = self.interpret_control_packet(packet)
                    if destination_id == self.receiver_id:
                        # Remove packet from the ring and keep a record of its information
                        self.receive_control_packet(packet=packet)
                        # Assign flag
                        self.control_packet_received = True
                        self.data_packet_received = False
                        # Assign data ring to tune to
                        self.tune_to_ring = packet[3]
                        self.tuned = False
            yield self.env.timeout(self.control_clock_cycle)

    def receive_on_data_ring(self):
        """
        Receiver process to remove a new data packet from the ring.

        TODO:
            * Determine the actual clock frequency for this subsystem

        This process operates at the unit clock frequency, and the data packet would only be from the \
        ring once its corresponding control packet has been received.

        In this process:

        1. The receiver takes ``'tuning_time'`` to tune to the data ring;
        2. The receiver waits and receives the data packet, \
        removes it from the ring and keeps a record of the transmission.
        """
        while True:
            # Check if a control packet is received
            if self.control_packet_received:
                # Tune to data ring if not yet tuned
                if not self.tuned:
                    self.tuned = True
                    yield self.env.timeout(self.model.constants.get('tuning_time'))
                present, packet = self.check_data_packet(ring_id=self.tune_to_ring)
                # Check if a data packet is detected
                if present:
                    # Remove packet from the ring and keep a record of its information
                    self.receive_data_packet(ring_id=self.tune_to_ring, packet=packet)
                    # Assign flag
                    self.data_packet_received = True
                    self.control_packet_received = False
            yield self.env.timeout(1)
