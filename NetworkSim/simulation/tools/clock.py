__all__ = ["TransmitterDataClock", "ReceiverDataClock", "ControlClock"]
__author__ = ["Hongyi Yang"]

import numpy as np

from NetworkSim.architecture.setup.model import Model


class TransmitterDataClock:
    """
    Synchronised clock for all transmitter on data rings.

    Parameters
    ----------
    model : Model
        The network model used in the simulation. Default is ``Model()``.

    Attributes
    ----------
    clock_cycle : float
        The clock cycle of the synchronised data clock.
    """

    def __init__(
            self,
            model=None
    ):
        if model is None:
            model = Model()
        self.model = model
        self.clock_cycle = self.get_clock_cycle()

    def get_clock_cycle(self):
        """
        Generate data packet transmission clock cycle.

        Returns
        -------
        clock_cycle : float
            The calculated clock cycle for data packet transmission.
        """
        # Calculate clock cycle and check if it is a good option for simulation
        if int(self.model.get_max_data_packet_num_on_ring()) & 1:
            raise ValueError('This configuration would result in data packet '
                             'transmission clock cycle not being a suitable number.')
        else:
            return self.model.circulation_time / self.model.get_max_data_packet_num_on_ring()


class ReceiverDataClock(TransmitterDataClock):
    """
    Synchronised clock for all receiver on data rings.

    Parameters
    ----------
    model : Model
        The network model used in the simulation. Default is ``Model()``.

    Attributes
    ----------
    clock_cycle : float
        The clock cycle of the synchronised data clock.
    """

    def __init__(
            self,
            model=None
    ):
        super().__init__(
            model=model
        )
        self.clock_cycle = self.get_clock_cycle()

    def get_clock_cycle(self):
        # Unoptimised
        # return super().get_clock_cycle() / self.model.network.num_nodes
        # Optimised
        return self.model.circulation_time / np.lcm(
            int(self.model.network.num_nodes),
            int(self.model.get_max_data_packet_num_on_ring())
        )


class ControlClock:
    """
    Synchronised clock for all transmitter and receiver on control ring.

    Parameters
    ----------
    model : Model
        The network model used in the simulation. Default is ``Model()``.

    Attributes
    ----------
    clock_cycle : float
        The clock cycle of the synchronised control clock.
    """

    def __init__(
            self,
            model=None
    ):
        if model is None:
            model = Model()
        self.model = model
        self.clock_cycle = self.get_clock_cycle()

    def get_clock_cycle(self):
        """
        Generate control packet transmission clock cycle.

        Returns
        -------
        clock_cycle : float
            The calculated clock cycle for control packet transmission.
        """
        # Calculate clock cycle and check if it is a good option for simulation
        if int(self.model.get_max_control_packet_num_on_ring()) & 1:
            raise ValueError("This configuration would result in control packet "
                             "transmission clock cycle not being a suitable number.")
        else:
            return self.model.circulation_time / self.model.get_max_control_packet_num_on_ring()
