__all__ = ["Simulator"]
__author__ = ["Hongyi Yang"]

import simpy
import pandas as pd
from joblib import Parallel, delayed

from NetworkSim.architecture.setup.model import Model
from NetworkSim.simulation.process.ram import RAM
from NetworkSim.simulation.process.transmitter.fixed import FT
from NetworkSim.simulation.process.receiver.tunable import TR


class Simulator:
    """
    Simulation wrapper to create a discrete event simulation of the ring network.

    Parameters
    ----------
    until : float
        The end time of the simulation.
    env: simpy Environment, optional
        The environment in which the simulation is carried out. Default is ``simpy.Environment()``
    model : Model, optional
        The network model used for the simulation. Default is ``Model()``.
    transmitter_type: str
        The type of transmitter used for the simulation, chosen from the list:

        - `fixed`: Fixed transmitter.

        Default is  ``"fixed"``.
    receiver_type: str
        The type of receiver used for the simulation, chosen from the list:

        - `tunable`: Tunable receiver.

        Default is  ``"tunable"``.
    """
    def __init__(
            self,
            until,
            env=None,
            model=None,
            transmitter_type="fixed",
            receiver_type="tunable"
    ):
        self.until = until
        if env is None:
            env = simpy.Environment()
        self.env = env
        if model is None:
            model = Model()
        self.transmitter_type = transmitter_type
        self.receiver_type = receiver_type
        self.model = model
        self.RAM = [None] * self.model.network.num_nodes
        self.transmitter = [None] * self.model.network.num_nodes
        self.receiver = [None] * self.model.network.num_nodes
        data = []
        self.latency_df = pd.DataFrame(data, columns=[
            'Source ID',
            'Destination ID',
            'Latency'
        ])
        self.error_df = pd.DataFrame(data, columns=[
            'Source ID',
            'Destination ID',
            'Error Timestamp'
        ])
        self.n_jobs = -1

    def initialise(self):
        """
        Initialisation of the simulation, where RAN, transmitter, and receiver processes are added to the environment.
        """

        def _initialise_ram(node_id):
            # Create RAM process
            self.RAM[node_id] = RAM(
                env=self.env,
                until=self.until,
                ram_id=node_id,
                model=self.model
            )
            # Initialise RAM process
            self.RAM[node_id].initialise()

        def _initialise_transmitter(node_id):
            # Create and initialise transmitter process
            if self.transmitter_type == "fixed":
                self.transmitter[node_id] = FT(
                    env=self.env,
                    ram=self.RAM[node_id],
                    transmitter_id=node_id,
                    model=self.model
                )
                self.transmitter[node_id].initialise()

        def _initialise_receiver(node_id):
            # Create and initialise receiver process
            if self.receiver_type == "tunable":
                self.receiver[node_id] = TR(
                    env=self.env,
                    until=self.until,
                    receiver_id=node_id,
                    model=self.model,
                    simulator=self
                )
            self.receiver[node_id].initialise()
        # Parallel
        Parallel(n_jobs=self.n_jobs, require='sharedmem')(
            delayed(_initialise_ram)(node_id) for node_id in range(self.model.network.num_nodes))
        Parallel(n_jobs=self.n_jobs, require='sharedmem')(
            delayed(_initialise_transmitter)(node_id) for node_id in range(self.model.network.num_nodes))
        Parallel(n_jobs=self.n_jobs, require='sharedmem')(
            delayed(_initialise_receiver)(node_id) for node_id in range(self.model.network.num_nodes))

    def run(self):
        """
        Run simulation.
        """
        self.env.run(until=self.until)
