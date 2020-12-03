[![Build and Test](https://img.shields.io/github/workflow/status/HYang1996/NetworkSim/Build%20and%20Test?logo=github)](https://github.com/HYang1996/NetworkSim/actions?query=workflow%3A%22Build+and+Test%22)

[![Documentation Status](https://readthedocs.org/projects/networksim/badge/?version=latest)](https://networksim.readthedocs.io/en/latest/)

[![PyPI version shields.io](https://img.shields.io/pypi/v/NetworkSim)](https://pypi.org/project/NetworkSim/)

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/HYang1996/NetworkSim/master?filepath=examples)

NetworkSim
==========

NetworkSim is a Python package used to simulation data transmission in a typical optical wavelength ring network using the Wavelength Division Multiplexing (WDM) technique.

.. figure:: docs/source/images/Ring-Network-Diagram.png
    :width: 400
    :align: center

    A typical WDM optical ring network in the data centre

Currently, two protocols have been implemented for the simulation, namely the fixed transmitter (FT) - tunable receiver (TR) protocol and the tunable transmitter (TT) - fixed receiver (FR) protocol.

Installation
------------

The package is available via PyPI using:

.. code-block:: bash

    pip install NetworkSim