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
    destination_ids : list
        A list of possible destination IDs on the ring.
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
        self.dis = Distribution(seed=ram_id, model=model)
        self.interarrival = self.get_interarrival()
        self.next_interarrival = 0
        self.queue = []
        self.destination_ids = self.get_destination_ids()

    def get_new_destination(self):
        """
        Function to return a new destination ID.

        Returns
        -------
        destination_id : int
            The ID of the new destination node.
        """
        return self.destination_ids[self.dis.uniform()]

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
        if self.distribution == 'pareto':
            return self.dis.pareto()
        if self.distribution == 'poisson':
            return self.dis.poisson()

    def generate_data_packet(self):
        """
        Data packet generation.

        Returns
        -------
        data_packet : str
            The data packet string in binary.
        """
        timestamp = self.env.now
        data_packet = self.model.data_signal.generate_packet()
        destination_id = self.get_new_destination()
        self.generated_data_packet_df = self.generated_data_packet_df.append({
            'Timestamp': timestamp,
            'Interarrival to Next': self.next_interarrival,
            'Raw Packet': data_packet,
            'Destination ID': destination_id
        }, ignore_index=True)
        self.queue.append([timestamp, data_packet, destination_id])

    def ram_traffic_generation(self):
        """
        Generation of RAM traffic as a simulation process.
        """
        while True:
            self.next_interarrival = self.get_interarrival()
            yield self.env.timeout(self.interarrival)
            self.generate_data_packet()
            self.interarrival = self.next_interarrival

    def initialise(self):
        """
        Initialisation of the RAM simulation.

        This function adds all RAM activities that will be used for the simulation, \
        including data sent to all nodes except for the node where the RAM sits, for the duration of the simulation.
        """
        self.env.process(self.ram_traffic_generation())
