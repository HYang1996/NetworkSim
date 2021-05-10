__all__ = ["TT_U"]
__author__ = ["Hongyi Yang"]

import numpy as np

from NetworkSim.simulation.process.transmitter.tunable import TT


class TT_U(TT):
    """
    Tunable transmitter simulator in bi-directional system, transmitting downstream packets.

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
        self.tuning_delay = self.get_upstream_tuning_delay()
        self.current_ring_id = self.transmitter_id

    def get_upstream_tuning_delay(self):
        downstream_tuning_delay = self.get_tuning_delay()
        # Initialise array
        tuning_delay = np.zeros((self.model.network.num_nodes, self.model.network.num_nodes))
        # Upstream tuning delay is calculated as downstream tuning delay with reversed source and destination
        for i in range(self.model.network.num_nodes):
            for j in range(self.model.network.num_nodes):
                tuning_delay[i][j] = downstream_tuning_delay[j][i]
        return tuning_delay

    def transmit_on_data_ring(self):
        """
        Tunable Transmitter process to add a new data packet onto the target ring in the upstream direction.

        In this process:

        1. The first data packet in the RAM queue is popped;
        2. The transmitter is tuned to the target ring
        3. Wait for correct timing to transmit
        4. The data packet is added onto its respective ring.
        """
        while self.env.now <= self.until:
            if self.ram.upstream_queue:
                # Remove packet from RAM queue
                _data_packet_wait_for_transmit = True
                generation_timestamp, data_packet, destination_id = self.get_packet_from_ram(is_upstream=True)
                # Tune to target data ring
                yield self.env.timeout(self.tuning_delay[self.current_ring_id][destination_id])
                self.current_ring_id = destination_id
                while _data_packet_wait_for_transmit:
                    if not self.ring_is_full(destination_id, reversed=True):
                        data_packet_present, _ = \
                            self.check_data_packet(destination_id, reversed=True)
                        if not data_packet_present:
                            # Transmit the data packet
                            self.transmit_data_packet(
                                ring_id=destination_id,
                                packet=data_packet,
                                destination_id=destination_id,
                                generation_timestamp=generation_timestamp,
                                reversed=True
                            )
                            _data_packet_wait_for_transmit = False
                    yield self.env.timeout(self._transmitter_data_clock_cycle)
            else:
                yield self.env.timeout(self._transmitter_data_clock_cycle)
