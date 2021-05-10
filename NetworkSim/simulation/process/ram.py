__all__ = ["RAM"]
__author__ = ["Hongyi Yang"]

from collections import deque

from NetworkSim.architecture.setup.model import Model
from NetworkSim.simulation.tools.distribution import Distribution


class RAM:
    """
    RAM process generation for simulation.

    Parameters
    ----------
    env : simpy Environment
        The simulation environment.
    until : float
        The end time of the simulation.
    ram_id : int
        The RAM ID.
    model : Model, optional
        The network model used for the simulation.
        Default is ``Model()``.
    distribution : str, optional
        The distribution chosen to generate the interarrival.
        Can be chosen from the following list:

        - 'pareto' : Pareto Distribution
        - 'poisson' : Poisson Distribution
    bidirectional : bool, optional
        If the system is bidirectional, default is ``False``. \
            If ``True``, `upstream_queue` and `downstream_queue` will be set up.
    seed : int, optional
        The seed used for source traffic generation. Default is ``1``.

    Attributes
    ----------
    generated_data_packet : list
        A list recording the information of the generated data packets in the RAM, containing the columns:

        - `Timestamp`
        - `Interarrival to Next`
        - `Raw Packet`
        - `Destination ID`
    queue : deque
        A queue containing the remaining data packets in the RAM for unidirectional transmission, with the fields:

        - `timestamp`
        - `data_packet`
        - `destination_id`
    upstream_queue : deque
        A queue containing the remaining data packets in the RAM  in the upstream direction \
            for bidirectional transmission, with the fields:

        - `timestamp`
        - `data_packet`
        - `destination_id`
    downstream_queue : deque
        A queue containing the remaining data packets in the RAM  in the downstream direction \
            for bidirectional transmission, with the fields:

        - `timestamp`
        - `data_packet`
        - `destination_id`
    queue_size_record : list
        A list of queue size record of the RAM, containing the columns:

        In the case of unidirectional transmission:

        - `timestamp`
        - `queue_length`

        In the case of bidirectional transmission:

        - `timestamp`
        - `upstream_queue_length`
        - `downstream_queue_length`
    """

    def __init__(
            self,
            env,
            until,
            ram_id,
            bidirectional,
            model=None,
            distribution='pareto',
            seed=1,
    ):
        self.env = env
        self.until = until
        self.ram_id = ram_id
        self.bidirectional = bidirectional
        if model is None:
            model = Model()
        self.model = model
        self.distribution_type = distribution
        self.generated_data_packet = []
        if self.bidirectional:
            self.upstream_queue = deque()
            self.downstream_queue = deque()
        else:
            self.queue = deque()
        self._distribution = Distribution(seed=seed * ram_id, model=model)
        self._interarrival = self.get_interarrival()
        self._next_interarrival = 0
        self._destination_ids = self.get_destination_ids()  # List of possible destination to send packets to
        self._abstract_data_id = 0  # Data ID counter when data packets are abstract
        self.add_to_queue_record = []
        self.pop_from_queue_record = []
        self.queue_size_record = []

    def get_new_destination(self):
        """
        Function to return a new destination ID.

        Returns
        -------
        destination_id : int
            The ID of the new destination node.
        """
        return self._destination_ids[self._distribution.uniform()]

    def get_destination_ids(self):
        """
        Function to generate a list of destination IDs to be chosen from.

        Returns
        -------
        destination_ids : list
            List of destination IDs.
        """
        destination_ids = []
        for i in range(self.model.network.num_nodes):
            if i != self.ram_id:
                destination_ids.append(i)
        return destination_ids

    def get_interarrival(self):
        """
        Get interarrival time statistics.

        Returns
        -------
        interarrival : float
            A new interval time
        """
        if self.distribution_type == 'pareto':
            return self._distribution.pareto()
        if self.distribution_type == 'poisson':
            return self._distribution.poisson()

    def is_upstream(self, destination_id):
        """
        Check if the destination node is an upstream node.

        Parameters
        ----------
        destination_id : int
            ID of the destination node.

        Returns
        -------
        is_upstream : bool
            ``True`` if the destination is upstream, ``False`` if downstream.
        """
        _difference = destination_id - self.ram_id
        if _difference < 0:
            _difference += self.model.network.num_nodes
        if _difference <= self.model.network.num_nodes / 2:
            return False
        else:
            return True

    def generate_data_packet(self):
        """
        Data packet generation.

        Returns
        -------
        data_packet : str
            The data packet string in binary.
        """
        timestamp = self.env.now
        if self.model.abstract:
            data_packet = [self.ram_id, self._abstract_data_id]
            self._abstract_data_id += 1
        else:
            data_packet = self.model.data_signal.generate_packet()
        destination_id = self.get_new_destination()
        self.generated_data_packet.append([
            timestamp,
            self._next_interarrival,
            data_packet,
            destination_id
        ])
        if self.bidirectional:
            if self.is_upstream(destination_id=destination_id):
                self.upstream_queue.append([timestamp, data_packet, destination_id])
            else:
                self.downstream_queue.append([timestamp, data_packet, destination_id])
        else:
            self.queue.append([timestamp, data_packet, destination_id])
        # For unit test
        self.add_to_queue_record.append([timestamp, data_packet, destination_id])

    def record_queue_size(self):
        """
        Record the current size of the RAM queue
        """
        if self.bidirectional:
            self.queue_size_record.append([self.env.now, len(self.upstream_queue), len(self.downstream_queue)])
        else:
            self.queue_size_record.append([self.env.now, len(self.queue)])

    def ram_traffic_generation(self):
        """
        Generation of RAM traffic as a simulation process.
        """
        while self.env.now <= self.until:
            self._next_interarrival = self.get_interarrival()
            yield self.env.timeout(self._interarrival)
            self.generate_data_packet()
            self.record_queue_size()
            self._interarrival = self._next_interarrival

    def initialise(self):
        """
        Initialisation of the RAM simulation.

        This function adds all RAM activities that will be used for the simulation, \
        including data sent to all nodes except for the node where the RAM sits, for the duration of the simulation.
        """
        self.env.process(self.ram_traffic_generation())
