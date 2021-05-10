__all__ = ["FR_U"]
__author__ = ["Hongyi Yang"]

from NetworkSim.simulation.process.receiver.base import BaseReceiver


class FR_U(BaseReceiver):
    """
    Fixed receiver simulator corresponding to upstream transmitters.

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

    def receive_on_data_ring(self):
        """
        Receiver process to remove a new data packet from the ring.

        This process operates at the unit clock frequency, and the data packet would be removed from the \
        ring whenever it is detected.

        In this process:
        1. The receiver waits and receives the data packet, \
        removes it from the ring and keeps a record of the transmission.
        2. The latency of the transmission is recorded.
        """
        while self.env.now <= self.until:
            # Check for packet if packet exist get it.
            present, packet = self.check_data_packet(ring_id=self.receiver_id, reversed=True)
            if present:
                # Remove packet from the ring and keep a record of its information
                self.record_error(packet, reversed=True)
                self.receive_data_packet(ring_id=self.receiver_id, packet=packet, reversed=True)
                # Wait for the end of the data packet
                yield self.env.timeout(self.model.data_packet_duration)
                # Record latency information
                self.record_latency(packet=packet)
                # Sync with clock
                yield self.env.timeout(self._time_compensation)
            else:
                # Receivers operate on same clock cycle as transmitters
                yield self.env.timeout(self._transmitter_data_clock_cycle)
