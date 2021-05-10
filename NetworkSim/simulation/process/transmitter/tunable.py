__all__ = ["TT"]
__author__ = ["Cheuk Ming Chung", "Hongyi Yang"]

import numpy as np

from NetworkSim.simulation.process.transmitter.base import BaseTransmitter


class TT(BaseTransmitter):
    """
    Tunable transmitter simulator.

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
            simulator,
            until,
            model=None):
        super().__init__(
            env=env,
            ram=ram,
            transmitter_id=transmitter_id,
            simulator=simulator,
            until=until,
            model=model
        )
        self.tuning_delay = self.get_tuning_delay()
        self.current_ring_id = self.transmitter_id

    def get_tuning_delay(self):
        """
        Function to calculate delay time required to tune from one data ring to another so that the transmission \
        is in sync with the reception on the specific data rings.

        Returns
        -------
        tuning_delay : float array
            A `n` by `n` float array of tuning delays. The row index represents the current ring ID while the column \
            index represents the target ring ID, where `n` is the total number of nodes/data rings in the network.
        """
        # Check if tuning delay has already been generated
        if self.simulator.TT_FR_tuning_delay is not None:
            return self.simulator.TT_FR_tuning_delay
        else:
            # Initialise array
            tuning_delay = np.zeros((self.model.network.num_nodes, self.model.network.num_nodes))
            # Calculate tuning delay time
            for i in range(self.model.network.num_nodes):
                for j in range(self.model.network.num_nodes):
                    if i != j:
                        # Distance from current node to the target node
                        _distance = self.model.network.get_distance(start=i, end=j)
                        # Transmission time in ns
                        _transmission_time = _distance / self.model.constants['speed'] * 1e9
                        # Delay time
                        tuning_delay[i][j] = self._transmitter_data_clock_cycle - np.round(
                            np.mod(_transmission_time, self._transmitter_data_clock_cycle),
                            decimals=1)
                        # Check if delay time is smaller than defined minimum tuning delay
                        if tuning_delay[i][j] < self.simulator.model.constants.get('tuning_time'):
                            # Delay until next available slot
                            tuning_delay[i][j] += self._transmitter_data_clock_cycle
            self.simulator.TT_FR_tuning_delay = tuning_delay
            return tuning_delay

    def transmit_on_data_ring(self):
        """
        Tunable Transmitter process to add a new data packet onto the target ring.

        In this process:

        1. The first data packet in the RAM queue is popped;
        2. The transmitter is tuned to the target ring
        3. Wait for correct timing to transmit
        4. The data packet is added onto its respective ring.
        """
        while self.env.now <= self.until:
            if self.ram.queue:
                # Remove packet from RAM queue
                _data_packet_wait_for_transmit = True
                generation_timestamp, data_packet, destination_id = self.get_packet_from_ram()
                # Tune to target data ring
                yield self.env.timeout(self.tuning_delay[self.current_ring_id][destination_id])
                self.current_ring_id = destination_id
                while _data_packet_wait_for_transmit:
                    if not self.ring_is_full(destination_id):
                        data_packet_present, _ = \
                            self.check_data_packet(destination_id)
                        if not data_packet_present:
                            # Transmit the data packet
                            self.transmit_data_packet(
                                ring_id=destination_id,
                                packet=data_packet,
                                destination_id=destination_id,
                                generation_timestamp=generation_timestamp
                            )
                            _data_packet_wait_for_transmit = False
                    yield self.env.timeout(self._transmitter_data_clock_cycle)
            else:
                yield self.env.timeout(self._transmitter_data_clock_cycle)
