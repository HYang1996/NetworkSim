.. _api_reference:

=============
API Reference
=============

.. autosummary::
    :toctree: modules/auto_generated/

.. include:: includes/api_css.rst

.. _architecture_ref:

Network Signal Configuration
============================

The :mod:`NetworkSim.architecture.signal` module contains definitions of the control and data signals used in the ring network.

.. automodule:: NetworkSim.architecture.signal
    :no-members:
    :no-inherited-members:

Signal Configuration
--------------------

.. currentmodule:: NetworkSim.architecture.signal

.. autosummary::
    :toctree: modules/auto_generated/
    :template: class.rst

    ControlSignal
    DataSignal

Network Architecture Base Configuration
=======================================

The :mod:`NetworkSim.architecture.base` module contains useful components for the configuration of the optical ring network hardware architecture.

.. automodule:: NetworkSim.architecture.base
    :no-members:
    :no-inherited-members:

Node Configuration
------------------

.. currentmodule:: NetworkSim.architecture.base.node

.. autosummary::
    :toctree: modules/auto_generated/
    :template: class.rst

    Node

Network Configuration
---------------------

.. currentmodule:: NetworkSim.architecture.base.network

.. autosummary::
    :toctree: modules/auto_generated/
    :template: class.rst

    Network

Ring Configuration
------------------

.. currentmodule:: NetworkSim.architecture.base.ring

.. autosummary::
    :toctree: modules/auto_generated/
    :template: class.rst

    Ring

Network Architecture Setup
=======================================

The :mod:`NetworkSim.architecture.setup` module enables integration of the network components into a complete network model.

.. automodule:: NetworkSim.architecture.setup
    :no-members:
    :no-inherited-members:

Model Configuration
-------------------

.. currentmodule:: NetworkSim.architecture.setup.model

.. autosummary::
    :toctree: modules/auto_generated/
    :template: class.rst

    Model

.. _simulation_ref:

Simulation Tools
================

The :mod:`NetworkSim.simulation.tools` module contains essential tools used for the simulation.

.. automodule:: NetworkSim.simulation.tools
    :no-members:
    :no-inherited-members:

Network Performance Analysis
----------------------------

.. currentmodule:: NetworkSim.simulation.tools.performance_analysis

.. autosummary::
    :toctree: modules/auto_generated/
    :template: function.rst

    get_transfer_delay
    get_throughput

Probability Distributions for Discrete Event Simulation
-------------------------------------------------------

.. currentmodule:: NetworkSim.simulation.tools.distribution

.. autosummary::
    :toctree: modules/auto_generated/
    :template: class.rst

    Distribution

Synchronised Clocks
-------------------

.. currentmodule:: NetworkSim.simulation.tools.clock

.. autosummary::
    :toctree: modules/auto_generated/
    :template: class.rst

    TransmitterDataClock
    ReceiverDataClock
    ControlClock

Simulation Information
----------------------

.. currentmodule:: NetworkSim.simulation.tools.info

.. autosummary::
    :toctree: modules/auto_generated/
    :template: class.rst

    Info

Simulation Summary
------------------

.. currentmodule:: NetworkSim.simulation.tools.summary

.. autosummary::
    :toctree: modules/auto_generated/
    :template: class.rst

    Summary

Simulation Processes
====================

The :mod:`NetworkSim.simulation.process` module contains essential processes used for the simulation.

.. automodule:: NetworkSim.simulation.process
    :no-members:
    :no-inherited-members:

RAM Process
-----------

.. currentmodule:: NetworkSim.simulation.process.ram

.. autosummary::
    :toctree: modules/auto_generated/
    :template: class.rst

    RAM

Transmitter Process
-------------------

.. currentmodule:: NetworkSim.simulation.process.transmitter

.. autosummary::
    :toctree: modules/auto_generated/
    :template: class.rst

    BaseTransmitter
    FT
    TT

Receiver Process
----------------

.. currentmodule:: NetworkSim.simulation.process.receiver

.. autosummary::
    :toctree: modules/auto_generated/
    :template: class.rst

    BaseReceiver
    FR
    TR

Simulation Setup
================

The :mod:`NetworkSim.simulation.simulator` module contains a wrapper to set up all necessary processes for the simulation.

.. automodule:: NetworkSim.simulation.simulator
    :no-members:
    :no-inherited-members:

Basic Simulation Wrapper
------------------------

.. currentmodule:: NetworkSim.simulation.simulator.base

.. autosummary::
    :toctree: modules/auto_generated/
    :template: class.rst

    BaseSimulator

Parallel Simulation
-------------------

.. currentmodule:: NetworkSim.simulation.simulator.parallel

.. autosummary::
    :toctree: modules/auto_generated/
    :template: class.rst

    ParallelSimulator



