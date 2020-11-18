__all__ = ["DataClock", "ControlClock"]
__author__ = ["Hongyi Yang"]

from NetworkSim.architecture.setup.model import Model


class DataClock:
    """
    Synchronised clock for all transmitter and receiver on data rings.

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
        # Calculate time for one circulation around the ring in ns
        circulation_time = self.model.network.length / self.model.constants.get('speed') * 1e9
        # Calculate clock cycle and check if it is a good option for simulation
        if self.model.get_max_data_packet_num_on_ring() % 2 != 0:
            raise ValueError('This configuration would result in data packet '
                             'transmission clock cycle not being a suitable number.')
        else:
            return circulation_time / self.model.get_max_data_packet_num_on_ring()


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
        # Calculate time for one circulation around the ring in ns
        circulation_time = self.model.network.length / self.model.constants.get('speed') * 1e9
        # Calculate clock cycle and check if it is a good option for simulation
        if self.model.get_max_control_packet_num_on_ring() % 2 != 0:
            raise ValueError('This configuration would result in control packet '
                             'transmission clock cycle not being a suitable number.')
        else:
            return circulation_time / self.model.get_max_control_packet_num_on_ring()
