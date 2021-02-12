__all__ = ["Distribution"]
__author__ = ["Hongyi Yang"]

import numpy as np

from NetworkSim.architecture.setup.model import Model


class Distribution:
    """
    Distribution class to generate interarrival time based on the chosen distribution.

    Parameters
    ----------
    model : Model, optional
        The network model used for simulation, containing network constants.
    seed : int, optional
        The randomisation seed.
        Default is ``0``.
    """

    def __init__(
            self,
            seed,
            model=None
    ):
        if model is None:
            model = Model()
        self.model = model
        self._pareto_position_parameter, self._pareto_shape_parameter = self.get_pareto_parameters()
        self._poisson_position_parameter, self._poisson_shape_parameter, self.poisson_lambda = \
            self.get_poisson_parameters()
        np.random.seed(seed)

    def uniform(self):
        """
        A uniform distribution to generate a new destination node ID.

        Returns
        -------
        index : int
            The index of the destination ID to be chosen.
        """
        return np.random.randint(low=0, high=self.model.network.num_nodes - 1)

    def get_poisson_parameters(self):
        """
        Calculation of Poisson distribution parameters,

        The interarrival time distribution follows a biased exponential distribution [3]_:

        .. math::
            f_T(t) = 0 \\quad t<a

            f_T(t) = b \\exp(-b(t-a)) \\quad t \\geq a


        where :math:`a\\geq 0` is the position parameter and :math:`b>0` is the shape parameter.

        For a source with average rate :math:`\\lambda_a` and burst rate :math:`\\sigma`:

        .. math::
            \\frac{1}{\\lambda_a} = a + \\frac{1}{b}

            b = \\frac{\\sigma \\lambda_a}{\\sigma - \\lambda_a}

        Returns
        -------
        interarrival : list
            A list of interarrival time in ns.

        References
        ----------
        .. [3] Gebali, F., 2008. Analysis of computer and communication networks. Springer Science & Business Media.
        """
        # Burst rate to each node, in packets/s
        _sigma = self.model.constants.get('maximum_bit_rate') / self.model.data_signal.size / 8
        # Position parameter, in ns
        position_parameter = 1 / _sigma
        # Shape parameter, in ns^-1 (average rate to to each node)
        _lambda_a = self.model.constants.get('average_bit_rate') / self.model.data_signal.size / 8
        shape_parameter = (_sigma * _lambda_a) / (_sigma - _lambda_a)
        return position_parameter, shape_parameter, _lambda_a

    def poisson(self):
        """
        Poisson distribution variate generation.

        Returns
        -------
        A new interarrival time calculated from the Poisson distribution.
        """
        return np.random.exponential(scale=1 / self._poisson_shape_parameter) + self._poisson_position_parameter

    def get_pareto_parameters(self):
        """
        Calculation of Pareto distribution parameters.

        Pareto distribution could be described by the pdf [1]_:

        .. math::
            f(x) = \\frac{ba^b}{x^{b+1}}

        where :math:`a` is the position parameter and :math:`b` is the shape parameter.

        The Hurst parameter is given by [2]_:

        .. math::
            H = \\frac{3 - b}{2}

        Parameters
        ----------
        hurst_parameter : float, optional
            The Hurst parameter for the Pareto distribution. Default is ``0.8`` [2]_. However, this parameter is not \
            in use currently as the average bit rate is used to calculate the shape parameter.

        Returns
        -------
        position_parameter : float
            The position parameter.
        shape_parameter : float
            The shape parameter.

        References
        ----------
        .. [1] Gebali, F., 2008. Analysis of computer and communication networks. Springer Science & Business Media.
        .. [2] So, W.H. and Kim, Y.C., 2007. Fair MAC protocol for optical ring network of wavelength-shared \
        access nodes. Photonic Network Communications, 13(3), pp.289-295.
        """
        # Calculate shape parameter
        _sigma = self.model.constants.get('maximum_bit_rate') / self.model.data_signal.size / 8
        _lambda_a = self.model.constants.get('average_bit_rate') / self.model.data_signal.size / 8
        shape_parameter = _sigma / (_sigma - _lambda_a)
        # Calculate position parameter
        position_parameter = 1 / _sigma
        return position_parameter, shape_parameter

    def pareto(self):
        """
        Pareto distribution variate generation.

        Returns
        -------
        A new interarrival time calculated from the Pareto distribution.
        """
        return (np.random.pareto(a=self._pareto_shape_parameter) + 1) * self._pareto_position_parameter
