import pandas as pd
import numpy as np

from NetworkSim.architecture.setup.model import Model
from NetworkSim.simulation.tools.distribution import Distribution

__all__ = ["RAM"]
__author__ = ["Hongyi Yang"]


class RAM:
    """
    RAM process generation for simulation.

    TODO:
        * Interarrival generation could be optimised by not generating the interarrival when i == ram_id

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
    generated_data_packet_df : pandas DataFrame
        A pandas DataFrame recording the information of the generated data packets in the RAM, containing the columns:

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
        self.distribution = distribution
        self.counter = np.zeros((self.model.network.num_nodes,), dtype=int)
        data = []
        self.generated_data_packet_df = pd.DataFrame(data, columns=[
            'Timestamp',
            'Interarrival to Next',
            'Raw Packet',
            'Destination ID'
        ])
        self.interarrival = [
            self.get_interarrival(seed=i)
            for i in range(self.model.network.num_nodes)
        ]
        self.queue = []

    def get_interarrival(self, seed):
        """
        Get interarrival time statistics.

        Parameters
        ----------
        seed : int
            The randomisation seed.

        Returns
        -------
        interarrival : list
            A list of interarrival time.
        """
        dis = Distribution(seed=seed)
        if self.distribution == 'pareto':
            return dis.pareto(until=self.until)
        if self.distribution == 'poisson':
            return dis.poisson(until=self.until)

    def generate_data_packet(self, destination_id, timestamp):
        """
        Data packet generation.

        Parameters
        ----------
        destination_id : int
            The node ID of the destination node.
        timestamp : float
            The timestamp when the data packet is generated.

        Returns
        -------
        data_packet : str
            The data packet string in binary.
        """
        # Check input type
        if not isinstance(destination_id, int):
            raise ValueError('Destination node ID must be an integer.')
        data_packet = self.model.data_signal.generate_packet()
        self.generated_data_packet_df = self.generated_data_packet_df.append({
            'Timestamp': timestamp,
            'Interarrival to Next': self.interarrival[destination_id][self.counter[destination_id]],
            'Raw Packet': data_packet,
            'Destination ID': destination_id
        }, ignore_index=True)
        self.queue.append([timestamp, data_packet, destination_id])

    def ram_traffic_generation(self, destination_id):
        """
        Generation of RAM traffic as a simulation process.

        Parameters
        ----------
        destination_id
            The destination ID.
        """
        while True:
            yield self.env.timeout(self.interarrival[destination_id][self.counter[destination_id]])
            self.counter[destination_id] += 1
            self.generate_data_packet(destination_id=destination_id, timestamp=self.env.now)

    def initialise(self):
        """
        Initialisation of the RAM simulation.

        This function adds all RAM activities that will be used for the simulation, \
        including data sent to all nodes except for the node where the RAM sits, for the duration of the simulation.
        """
        for i in range(self.model.network.num_nodes):
            if i != self.ram_id:
                self.env.process(self.ram_traffic_generation(destination_id=i))
