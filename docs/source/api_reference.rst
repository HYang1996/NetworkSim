.. _api_reference:

=============
API Reference
=============

.. autosummary::
    :toctree: modules/auto_generated/

.. include:: includes/api_css.rst

.. _architecture_ref:

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

    DataClock
    ControlClock

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

Receiver Process
----------------

.. currentmodule:: NetworkSim.simulation.process.receiver

.. autosummary::
    :toctree: modules/auto_generated/
    :template: class.rst

    BaseReceiver
    TR

Simulation Setup
================

The :mod:`NetworkSim.simulation.setup` module contains a wrapper to set up all necessary processes for the simulation.

.. automodule:: NetworkSim.simulation.setup
    :no-members:
    :no-inherited-members:

Simulation Wrapper
------------------

.. currentmodule:: NetworkSim.simulation.setup.simulator

.. autosummary::
    :toctree: modules/auto_generated/
    :template: class.rst

    Simulator


