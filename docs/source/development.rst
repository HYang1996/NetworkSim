Development Guide
=================

Workflow
--------
#. Writing new classes and methods
    #. Update new files in the ``REAMDE\Package Structure`` section
    #. Include comments and docstrings in the codes
    #. Create or improve example notebooks whenever necessary
    #. Create unit tests whenever necessary and verify locally
#. Formatting
    #. Use flake8 for formatting checks
#. Documentation
    #. Include docstrings for all classes and functions
    #. Use Sphinx for documentation

Usage
-----

Directory Tree
~~~~~~~~~~~~~~
Generate the package directory tree:

.. code-block:: bash

    tree NetworkSim -I '__pycache__|*.pyc|__init__*'

Formatting
~~~~~~~~~~

Run flake8 for formatting checks:

.. code-block:: bash

    flake8 NetworkSim/

Tests
~~~~~

Run tests in a module:

.. code-block:: bash

    pytest test_example.py


Run tests in a directory:

.. code-block:: bash

    pytest example_directory/


Run all unit tests:

.. code-block:: bash

    pytest NetworkSim/


Note, if `ModuleNotFoundError: No module named 'NetworkSim'` is raised, use the alternative command followed by the test directory:

.. code-block:: bash

    python3 -m pytest


Documentation
~~~~~~~~~~~~~

The documentation of this project is build using Sphinx.

Go to the `docs` directory:

.. code-block:: bash

    cd docs

Run the command to build documentation files:

.. code-block:: bash

    make clean html

View the documentation web page:

.. code-block:: bash

    open build/html/index.html
