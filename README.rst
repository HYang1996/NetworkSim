.. -*- mode: rst -*-

|github|_ |readthedocs|_ |pypi|_ |binder|_

.. |github| image:: https://img.shields.io/github/workflow/status/HYang1996/NetworkSim/Build%20and%20Test?logo=github
.. _github: https://github.com/HYang1996/NetworkSim/actions?query=workflow%3A%22Build+and+Test%22

.. |readthedocs| image:: https://readthedocs.org/projects/networksim/badge/?version=latest
.. _readthedocs: https://networksim.readthedocs.io/en/latest/

.. |pypi| image:: https://img.shields.io/pypi/v/NetworkSim
.. _pypi: https://pypi.org/project/NetworkSim/

.. |binder| image:: https://mybinder.org/badge_logo.svg
.. _binder: https://mybinder.org/v2/gh/HYang1996/NetworkSim/master?filepath=examples

NetworkSim
==========

NetworkSim is a Python package used to simulation data transmission in a typical optical wavelength ring network using the Wavelength Division Multiplexing (WDM) technique:

.. image:: docs/source/images/Ring-Network-Diagram.png
    :width: 800
    :align: center


Currently, two protocols have been implemented for the simulation, namely the fixed transmitter (FT) - tunable receiver (TR) protocol and the tunable transmitter (TT) - fixed receiver (FR) protocol.

Installation
------------

The package is available via PyPI using:

.. code-block:: bash

    pip install NetworkSim

Quickstart
----------

.. code-block:: python

    from NetworkSim import BaseSimulator

Documentation
-------------

Read the detailed package `API reference <https://networksim.readthedocs.io/en/latest/>`__.