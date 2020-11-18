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
            model=None,
            seed=0
    ):
        if model is None:
            model = Model()
        self.model = model
        self.seed = seed

    def poisson(self, until):
        """
        Poisson traffic source.

        The interarrival time distribution follows a biased exponential distribution [3]_:

        .. math::
            f_T(t) = 0 \\quad t<a

            f_T(t) = b \\exp(-b(t-a)) \\quad t \\geq a


        where :math:`a\\geq 0` is the position parameter and :math:`b>0` is the shape parameter.

        For a source with average rate :math:`\\lambda_a` and burst rate :math:`\\sigma`:

        .. math::
            \\frac{1}{\\lambda_a} = a + \\frac{1}{b}

            b = \\frac{\\sigma \\lambda_a}{\\sigma - \\lambda_a}

        Parameters
        ----------
        until : int
            Finished time of the simulation in ns.

        Returns
        -------
        interarrival : list
            A list of interarrival time in ns.

        References
        ----------
        .. [3] Gebali, F., 2008. Analysis of computer and communication networks. Springer Science & Business Media.
        """

        # initialise seed and parameters
        np.random.seed(self.seed)
        interarrival = [0]
        # Burst rate, in packets/s
        sigma = self.model.constants.get('maximum_bit_rate') / self.model.data_signal.size / 8
        # Position parameter, in ns
        a = 1 / sigma
        # Shape parameter, in ns^-1
        lambda_a = self.model.constants.get('average_bit_rate') / self.model.data_signal.size / 8
        b = (sigma * lambda_a) / (sigma - lambda_a)
        while np.sum(interarrival) <= until:
            new_interarrival = np.random.exponential(scale=1 / b) + a
            interarrival.append(new_interarrival)
        return interarrival[1:]

    def pareto(self, until, hurst_parameter=0.8):
        """
        Pareto distribution variate generation.

        Pareto distribution could be described by the pdf [1]_:

        .. math::
            f(x) = \\frac{ba^b}{x^{b+1}}

        where :math:`a` is the position parameter and :math:`b` is the shape parameter.

        The Hurst parameter is given by [2]_:

        .. math::
            H = \\frac{3 - b}{2}

        Parameters
        ----------
        until : float
            Finished time of the simulation in ns.
        hurst_parameter : float, optional
            The Hurst parameter for the Pareto distribution. Default is ``0.8`` [2]_. However, this parameter is not \
            in use currently as the average bit rate is used to calculate the shape parameter.

        Returns
        -------
        interarrival : list
            A list of interarrival time in ns.

        References
        ----------
        .. [1] Gebali, F., 2008. Analysis of computer and communication networks. Springer Science & Business Media.
        .. [2] So, W.H. and Kim, Y.C., 2007. Fair MAC protocol for optical ring network of wavelength-shared \
        access nodes. Photonic Network Communications, 13(3), pp.289-295.
        """
        # initialise seed and parameters
        np.random.seed(self.seed)
        interarrival = [0]
        # Calculate shape parameter
        # b = 3 - 2 * hurst_parameter
        sigma = self.model.constants.get('maximum_bit_rate') / self.model.data_signal.size / 8
        lambda_a = self.model.constants.get('average_bit_rate') / self.model.data_signal.size / 8
        b = sigma / (sigma - lambda_a)
        # Calculate position parameter
        a = 1 / sigma
        while np.sum(interarrival) <= until:
            new_interarrival = (np.random.pareto(a=b) + 1) * a
            interarrival.append(new_interarrival)
        return interarrival[1:]
