Molecular Dynamics
==================

.. module:: ase_md

Overview
--------

SPARC run MD simulation leveraging the ASE `MD engine <https://ase-lib.org/ase/md.html>`_ framework.
It supports both *ab initio* MD (AIMD) and machine-learning MD (ML-MD) using DeepPotential models.  
This module integrates thermostats, logging, checkpointing, and trajectory handling into a unified workflow.

It currently supports the NVT ensemble with ``Langevin`` thermostat or the ``Nosé-Hoover chain`` thermostat. Parameters such as damping time (for ``Nose``) or friction coefficient (``Langevin``) needs to defined.

Each ML/MD iteration is saved in the corresponding ``iter_0000xx/02.dpmd`` directory, which includes the simulation log (``log_file``), the trajectory of atomic positions (``extxyz`` or ``traj``).  It also write a checkpoint file to restart long simulations.

Simulation Outputs
-----------------

.. code-block:: bash

    >>> cat Iter1_dpmd.log
    Time[ps]      Etot[eV]     Epot[eV]     Ekin[eV]    T[K]
    0.0000        -112.0807    -112.8950       0.8143   300.0
    0.0700        -111.6322    -112.7149       1.0828   398.9
    0.1400        -112.4215    -113.3518       0.9303   342.7
    0.2100        -112.9996    -113.6775       0.6779   249.8
    0.2800        -112.6910    -113.7220       1.0310   379.8
    0.3500        -112.8007    -113.2903       0.4896   180.4

.. Module Contents
.. ---------------

.. .. automodule:: src.ase_md
..     :members:
..     :undoc-members:
..     :show-inheritance:

.. Functions:
.. ----------

.. .. autofunction:: sparc.src.ase_md.NoseNVT

.. .. autofunction:: sparc.src.ase_md.LangevinNVT


Usage Examples
--------------

- Nose-Hoover NVT Simulation:

.. autofunction:: sparc.src.ase_md.NoseNVT

.. code-block:: python

    from ase import Atoms
    from sparc.src.ase_md import NoseNVT

    atoms = Atoms("H2O")
    dyn = NoseNVT(atoms, temperature=300)
    dyn.run(1000)

- Langevin NVT Simulation:

.. autofunction:: sparc.src.ase_md.LangevinNVT

.. code-block:: python

    from sparc.src.ase_md import LangevinNVT

    dyn = LangevinNVT(atoms, temperature=300, friction=0.01)
    dyn.run(1000)

- Ab-initio Molecular Dynamics:

.. autofunction:: sparc.src.ase_md.ExecuteAbInitioDynamics

.. code-block:: python

    from sparc.src.ase_md import ExecuteAbInitioDynamics

    ExecuteAbInitioDynamics(system=atoms, dyn=dyn, steps=500, pace=10, 
                            log_filename="aimd.log", trajfile="aimd.traj", 
                            dir_name="aimd_results", name="DFT_AIMD")

References
----------

For more information on ASE, visit: https://wiki.fysik.dtu.dk/ase/
