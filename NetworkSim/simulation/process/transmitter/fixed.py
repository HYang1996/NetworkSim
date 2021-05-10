__all__ = ["FT"]
__author__ = ["Hongyi Yang"]

from NetworkSim.simulation.process.transmitter.base import BaseTransmitter


class FT(BaseTransmitter):
    """
    Fixed transmitter simulator.

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
        super().__init__(
            env=env,
            ram=ram,
            transmitter_id=transmitter_id,
            simulator=simulator,
            until=until,
            model=model
        )
        self.control_packet_transmitted = False
        self.data_packet_transmitted = True

    def transmit_on_control_ring(self):
        """
        Fixed Transmitter process to add a new control packet onto the ring.

        This process operates at the transmission data clock frequency. Ring slot check is performed on both \
        the control and the data ring.

        In this process:

        1. The first data packet in the RAM queue is peeked;
        2. A new control packet is generated based on the data packet information;
        3. The control packet is added to the control ring when a slot is available;
        4. The subsystem informs the data transmitter to start transmission.
        """
        while self.env.now <= self.until:
            # Check if RAM is not empty and if previous data packet has been transmitted
            if self.ram.queue and not self.ring_is_full(self.transmitter_id):
                # Check if both control and data rings are available
                control_packet_present, control_packet = self.check_control_packet()
                data_packet_present, _ = self.check_data_packet(self.transmitter_id)
                if not control_packet_present and not data_packet_present:
                    # Obtain packet information in the queue
                    generation_timestamp, _, destination_id = self.ram.queue[0]
                    # Generate control packet
                    control_packet = self.generate_control_packet(destination=destination_id, control=0)
                    # Transmit the control packet
                    self.transmit_control_packet(
                        packet=control_packet,
                        destination_id=destination_id,
                        generation_timestamp=generation_timestamp
                    )
                    self.control_packet_transmitted = True
            yield self.env.timeout(self._transmitter_data_clock_cycle)

    def transmit_on_data_ring(self):
        """
        Fixed Transmitter process to add a new data packet onto the ring.

        For FT-TR model.

        In this process:

        1. The first data packet in the RAM queue is popped;
        2. The data packet is added onto its respective ring.
        """
        while self.env.now <= self.until:
            # Check if a control packet has been transmitted
            if self.control_packet_transmitted:
                # Remove packet from RAM queue
                generation_timestamp, data_packet, destination_id = self.ram.queue.popleft()
                self.ram.record_queue_size()
                # For unit test
                self.ram.pop_from_queue_record.append([generation_timestamp, data_packet, destination_id])
                # Transmit the data packet
                self.transmit_data_packet(
                    ring_id=self.transmitter_id,
                    packet=data_packet,
                    destination_id=destination_id,
                    generation_timestamp=generation_timestamp
                )
                self.control_packet_transmitted = False
            yield self.env.timeout(self._transmitter_data_clock_cycle)
