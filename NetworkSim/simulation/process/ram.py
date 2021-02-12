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

    Attributes
    ----------
    generated_data_packet : list
        A list recording the information of the generated data packets in the RAM, containing the columns:

        - `Timestamp`
        - `Interarrival to Next`
        - `Raw Packet`
        - `Destination ID`
    queue : queue
        A queue containing the remaining data packets in the RAM, with the fields:

        - `timestamp`
        - `data_packet`
        - `destination_id`
    """

    def __init__(
            self,
            env,
            until,
            ram_id,
            model=None,
            distribution='pareto'
    ):
        self.env = env
        self.until = until
        self.ram_id = ram_id
        if model is None:
            model = Model()
        self.model = model
        self.distribution_type = distribution
        self.generated_data_packet = []
        self.queue = deque()
        self._distribution = Distribution(seed=ram_id, model=model)
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
        self.queue.append([timestamp, data_packet, destination_id])
        # For unit test
        self.add_to_queue_record.append([timestamp, data_packet, destination_id])

    def record_queue_size(self):
        """
        Record the current size of the RAM queue
        """
        self.queue_size_record.append([self.env.now, len(self.queue)])

    def ram_traffic_generation(self):
        """
        Generation of RAM traffic as a simulation process.
        """
        while True:
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
