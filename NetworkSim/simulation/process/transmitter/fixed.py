__all__ = ["FT"]
__author__ = ["Hongyi Yang"]

from NetworkSim.simulation.process.transmitter.base import BaseTransmitter


class FT(BaseTransmitter):
    """
    Fixed Transmitter simulator.

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
            model=None):
        super().__init__(
            env=env,
            ram=ram,
            transmitter_id=transmitter_id,
            model=model
        )
        self.control_packet_transmitted = False
        self.data_packet_transmitted = True

    def transmit_on_control_ring(self):
        """
        Fixed Transmitter process to add a new control packet onto the ring.

        This process operates at the control clock frequency, and the control packet would only be added onto the \
        ring after a previous data packet has been sent. A ring slot check would also be performed before \
        adding the packet to the ring.

        In this process:

        1. The first data packet in the RAM queue is peeked;
        2. A new control packet is generated based on the data packet information;
        3. The control packet is added onto the control ring when the ring slot is available;
        4. The `self.transmitted_control_packet_df` keeps a record of this control packet.
        """
        while True:
            # Check if RAM is not empty and if previous data packet has been transmitted
            if len(self.ram.queue) != 0 and self.data_packet_transmitted:
                # Check if data ring is full
                if not self.ring_is_full():
                    present, packet = self.check_control_packet()
                    # Check if a control ring slot is available
                    if not present:
                        # Obtain packet information in the queue
                        timestamp, data_packet, destination_id = self.ram.queue[0]
                        # Generate control packet
                        control_packet = self.generate_control_packet(destination=destination_id, control=0)
                        # Transmit the control packet
                        self.transmit_control_packet(packet=control_packet, destination_id=destination_id)
                        # Assign flag
                        self.control_packet_transmitted = True
                        self.data_packet_transmitted = False
            yield self.env.timeout(self.control_clock_cycle)

    def transmit_on_data_ring(self):
        """
        Fixed Transmitter process to add a new data packet onto the ring.

        This process operates at the data clock frequency, and the data packet would only be added onto the \
        ring once its corresponding control packet has been sent. A ring slot check would also be performed before \
        adding the packet to the ring.

        In this process:

        1. The first data packet in the RAM queue is dequeued;
        2. The data packet is added onto the corresponding data ring;
        3. The `self.transmitted_data_packet_df` keeps a record of this data packet.
        """
        while True:
            # Check if a control packet has been transmitted
            if self.control_packet_transmitted:
                present, packet = self.check_data_packet()
                # Check if a data ring slot is available
                if not present:
                    # Obtain packet information in the queue and dequeue packet
                    timestamp, data_packet, destination_id = self.ram.queue.pop(0)
                    # Transmit the data packet
                    self.transmit_data_packet(packet=data_packet, destination_id=destination_id)
                    # Assign flags
                    self.data_packet_transmitted = True
                    self.control_packet_transmitted = False
            yield self.env.timeout(self.data_clock_cycle)
