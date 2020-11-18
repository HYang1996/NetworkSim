__all__ = ["Simulator"]
__author__ = ["Hongyi Yang"]

import simpy

from NetworkSim.architecture.setup.model import Model
from NetworkSim.simulation.process.ram import RAM
from NetworkSim.simulation.process.transmitter.fixed import FT
from NetworkSim.simulation.process.receiver.tunable import TR


class Simulator:
    """
    Simulation wrapper to create a discrete event simulation of the ring network.

    TODO:
        * Initialisation could be parallelised for better performance

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
        self.RAM = []
        self.transmitter = []
        self.receiver = []

    def initialise(self):
        """
        Initialisation of the simulation, where RAN, transmitter, and receiver processes are added to the environment.
        """
        for i in range(self.model.network.num_nodes):
            # Create RAM processes
            self.RAM.append(
                RAM(
                    env=self.env,
                    until=self.until,
                    ram_id=i,
                    model=self.model
                )
            )
            self.RAM[i].initialise()
            # Create transmitter processes
            if self.transmitter_type == "fixed":
                self.transmitter.append(
                    FT(
                        env=self.env,
                        ram=self.RAM[i],
                        transmitter_id=i,
                        model=self.model
                    )
                )
            self.transmitter[i].initialise()
            # Create receiver processes
            if self.receiver_type == "tunable":
                self.receiver.append(
                    TR(
                        env=self.env,
                        receiver_id=i,
                        model=self.model
                    )
                )
            self.receiver[i].initialise()

    def run(self):
        """
        Run simulation.
        """
        self.env.run(until=self.until)
