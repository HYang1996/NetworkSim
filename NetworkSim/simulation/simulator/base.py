__all__ = ["BaseSimulator"]
__author__ = ["Hongyi Yang"]

from timeit import default_timer as timer

import simpy
import pandas as pd
from tqdm.auto import trange

from NetworkSim.architecture.setup.model import Model
from NetworkSim.simulation.process.ram import RAM
from NetworkSim.simulation.process.receiver.fixed import FR
from NetworkSim.simulation.process.receiver.tunable import TR
from NetworkSim.simulation.process.transmitter.fixed import FT
from NetworkSim.simulation.process.transmitter.tunable import TT
from NetworkSim.simulation.tools.info import Info
from NetworkSim.simulation.tools.summary import Summary


class BaseSimulator:
    """
    Simulation wrapper to create a discrete event simulation of the ring network.

    Parameters
    ----------
    until : float
        The end time of the simulation.
    env: simpy Environment, optional
        The environment in which the simulation is carried out. Default is ``simpy.Environment()``.
    model : Model, optional
        The network model used for the simulation. Default is ``Model()``.
    transmitter_type: str
        The type of transmitter used for the simulation, chosen from the list:

        - `fixed`, `f` or `F`
            Fixed transmitter.
        - `tunable`, `t` or `T`
            Tunable transmitter.

        Default is  ``tunable``.
    receiver_type: str
        The type of receiver used for the simulation, chosen from the list:

        - `fixed`, `f` or `F`
            Fixed receiver.
        - `tunable`, `t`, or `T`
            Tunable receiver.

        Default is  ``fixed``.
    traffic_generation_method : str
        The method used for generate source traffic, chosen from the list:

        - `poisson`
            Poisson distribution.
        - `pareto`
            Pareto distribution.

        Default is ``poisson``.
    Attributes
    ----------
    latency : list
        A list of packet transmission latency recorded during the simulation, containing the keys:

        - `Latency Timestamp` : float
            The timestamp when the latency is recorded.
        - `Source ID` : int
            The ID of the source node.
        - `Destination ID` : int
            The ID of the destination node.
        - `Queueing Delay : float
            The recorded queueing delay latency.
        - `Transfer Delay : float
            The recorded transfer delay latency.
        - `Data Rate` : float
            The data rate recorded as the operation is completed.

    error : list
        A list of transmission errors occurred during the simulation, containing the keys:

        - `Error Timestamp` : float
            The timestamp when the error occurred.
        - `Source ID` : int
            The ID of the source node.
        - `Destination ID` : int
            The ID of the destination node.
        - `Error Type` : str
            The type of error recorded.
    """

    def __init__(
            self,
            until,
            env=None,
            model=None,
            transmitter_type=None,
            receiver_type=None,
            traffic_generation_method=None
    ):
        self.until = until
        if env is None:
            env = simpy.Environment()
        self.env = env
        if model is None:
            model = Model()
        if transmitter_type is None:
            transmitter_type = 'T'
        if receiver_type is None:
            receiver_type = 'F'
        if traffic_generation_method is None:
            traffic_generation_method = 'poisson'
        self.transmitter_type = transmitter_type
        self.receiver_type = receiver_type
        self.traffic_generation_method = traffic_generation_method
        self.model = model
        self.RAM = [None] * self.model.network.num_nodes
        self.transmitter = [None] * self.model.network.num_nodes
        self.receiver = [None] * self.model.network.num_nodes
        self._fixed_keywords = {'fixed', 'f', 'F'}
        self._tunable_keywords = {'tunable', 't', 'T'}
        self.runtime = None
        self.latency = []
        self.error = []
        self.TT_FR_tuning_delay = None
        self.ram_queue_delay = []

    def _initialise_ram(self, node_id):
        """
        RAM initialisation.

        Parameters
        ----------
        node_id : int
            Id of the node (RAM).
        """
        # Create RAM process
        self.RAM[node_id] = RAM(
            env=self.env,
            until=self.until,
            ram_id=node_id,
            model=self.model,
            distribution=self.traffic_generation_method
        )
        # Initialise RAM process
        self.RAM[node_id].initialise()

    def _initialise_transmitter(self, node_id):
        """
        Transmitter initialisation.

        Parameters
        ----------
        node_id : int
            ID of the node (transmitter).
        """
        # Create and initialise transmitter process
        if self.transmitter_type in self._fixed_keywords:
            self.transmitter[node_id] = FT(
                env=self.env,
                ram=self.RAM[node_id],
                transmitter_id=node_id,
                model=self.model,
                simulator=self
            )
        elif self.transmitter_type in self._tunable_keywords:
            self.transmitter[node_id] = TT(
                env=self.env,
                ram=self.RAM[node_id],
                transmitter_id=node_id,
                model=self.model,
                simulator=self
            )
        else:
            raise NotImplementedError("Transmitter type not implemented.")
        self.transmitter[node_id].initialise()

    def _initialise_receiver(self, node_id):
        """
        Receiver initialisation.

        Parameters
        ----------
        node_id : int
            ID of the node (receiver).
        """
        # Create and initialise receiver process
        if self.receiver_type in self._fixed_keywords:
            self.receiver[node_id] = FR(
                env=self.env,
                until=self.until,
                receiver_id=node_id,
                model=self.model,
                simulator=self
            )
        elif self.receiver_type in self._tunable_keywords:
            self.receiver[node_id] = TR(
                env=self.env,
                until=self.until,
                receiver_id=node_id,
                model=self.model,
                simulator=self
            )
        else:
            raise NotImplementedError("Receiver type not implemented.")
        self.receiver[node_id].initialise()

    def initialise(self):
        """
        Initialisation of the simulation, where RAM, transmitter, and receiver processes are added to the environment.
        """
        # Check if the combination is implemented
        if self.transmitter_type in self._fixed_keywords and self.receiver_type in self._fixed_keywords:
            raise NotImplementedError("The FT-FR model is not implemented.")
        if self.transmitter_type in self._tunable_keywords and self.receiver_type in self._tunable_keywords:
            raise NotImplementedError("The TT-TR model is not implemented.")
        # Initialise all three subsystems
        for node_id in range(self.model.network.num_nodes):
            self._initialise_ram(node_id=node_id)
            self._initialise_transmitter(node_id=node_id)
            self._initialise_receiver(node_id=node_id)

    def run(self):
        """
        Run simulation.
        """
        _start_time = timer()
        for i in trange(1, self.until):
            self.env.run(until=i)
        _end_time = timer()
        self.runtime = _end_time - _start_time

    def info(
            self,
            info_type=None,
            component_type=None,
            component_id=None):
        """
        Obtain information of simulation components. Check `Info` class fore more details.

        Parameters
        ----------
        info_type : str
            The type of information requested, chosen from the following:

            - `control` or `c`
                Information on control ring. When `device_type == None`, this returns all packet transmission \
                information on the control ring, otherwise it refers to control packets transmitted by a transmitter \
                or control packets received by a receiver. `component_id` is not required in this case.
            - `data` or `d`
                Information on data ring. When `device_type == None`, this returns all packet transmission \
                information on the data ring, otherwise it refers to data packets transmitted by a transmitter \
                or data packets received by a receiver. An `component_id` must be specified in this case.

        component_type : str
            The type of component in the simulation, chosen from the following:

            - `ram` or `RAM`
                Transmitter RAM information, where data packets are generated. An `component_id` must be specified \
                in this case, but `info_type` is not required.
            - `transmitter` or `t`
                Transmitter packet information. Both `component_id` and `info_type` must be specified.
            - `receiver` or `r`
                Receiver packet information. Both `component_id` and `info_type` must be specified.

        component_id : int
            The ID of the component of choice.

        Returns
        -------
        info : pandas DataFrame
            A DataFrame containing the information requested.
        """
        _ram_keywords = {'ram', 'RAM'}
        _transmitter_keywords = {'transmitter', 't'}
        _receiver_keywords = {'receiver', 'r'}
        _info = Info(simulator=self)
        if component_type is None:
            return _info.ring_info(ring_id=component_id, info_type=info_type)
        elif component_type in _ram_keywords:
            return _info.ram_info(device_id=component_id)
        elif component_type in _transmitter_keywords:
            return _info.transmitter_info(device_id=component_id, info_type=info_type)
        elif component_type in _receiver_keywords:
            return _info.receiver_info(device_id=component_id, info_type=info_type)
        else:
            raise ValueError("Type of information requested is not recognised.")

    def summary(self, summary_type=None, format='df'):
        """
        Obtain a summary of the simulation performed. Refer to `Summary` class for more details.

        Parameters
        ----------
        summary_type : str, optional
            The type of summary, chosen from the following:

            - `None`
                No `summary_type` input, and a generic summary is returned.
            - `latency` or `l`
                Latency summary, with latency information for all source-destination combinations.
            - `ram` or `RAM`
                Transmitter RAM data generation summary.
            - `transmitter` or `t`
                Transmitter summary.
            - `receiver` or `r`
                Receiver summary.
        format : str, optional
            The format of the summary, chosen from the following:

            - `df`
                Return a pandas DataFrame, which is the default output format.
            - `csv`
                Export a summary of the simulation performed as a csv file. Refer to `Summary` class for more details.
            - `plot`
                A plot of the summary selected.
        """
        _latency_keywords = {'latency', 'l'}
        _ram_keywords = {'ram', 'RAM'}
        _transmitter_keywords = {'transmitter', 't'}
        _receiver_keywords = {'receiver', 'r'}
        _summary = Summary(simulator=self)
        summary_df = None
        _summary_name = None
        if summary_type is None:
            summary_df = _summary.simulation_summary()
            summary_type = 'simulation'
        elif summary_type in _ram_keywords:
            summary_df = _summary.ram_summary()
        elif summary_type in _transmitter_keywords:
            summary_df = _summary.transmitter_summary()
        elif summary_type in _receiver_keywords:
            summary_df = _summary.receiver_summary()
        elif summary_type in _latency_keywords:
            summary_df = _summary.latency_summary()
        else:
            raise ValueError("Summary type is not recognised.")
        # Output summary based on format selected
        if format == 'df':
            return summary_df
        elif format == 'csv':
            _summary_name = summary_type
            _file_name = _summary_name + "_summary.csv"
            summary_df.to_csv(_file_name, index=False)
        elif format == 'plot':
            raise NotImplementedError("Plot has not been implemented.")
        else:
            raise ValueError("Output format not recognised.")

    def export_data_as_csv(self, file_name=None, data=None, index=None, columns=None):
        """
        Export a python list as a csv file.

        Parameters
        ----------
        file_name: string
            Name of the output csv file

        data : ndarray (structured or homogeneous), Iterable, dict, or DataFrame
            The data to be exported as csv file

        index: list, optional
            Index to use for resulting csv file

        columns: list, optional
            Column labels to use for csv file
        """
        if not isinstance(file_name, str):
            raise ValueError("file_name must be a string.")
        elif file_name.rfind(".csv", -4) == -1:
            file_name = file_name + ".csv"
        df = pd.DataFrame(data, columns=columns, index=index)
        row_names = False
        if index:
            row_names = True
        df.to_csv(file_name, index=row_names)
