.. default-role:: math

Tutorial
========

.. module:: tutorial


Welcome to SPARC tutorial.!

Example: PES scan in Ammonia Borate (NH\ :math:`_3`\ BH\ :math:`_3`)
---------------------------------------------------------------------


.. .. image:: "_static/AmmoniaBorate.png"

.. raw:: html 

   <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 20px;">
      <img src="_static/AmmoniaBorate.png" alt="" style="height: 120px; object-fit: contain;">
   </div>

.. contents:: Table of Contents
   :depth: 2
   :local:

Introduction
------------

In this tutorial, we demonstrate how to run the **SPARC** workflow. We will show how to:

.. to build a ML potential and then later use that to study the dissociation of B-N bond. 

1. Prepare input files, see section :ref:`inputfile` for details,
2. Prepare data,
3. Train ML potential models with DeepMD-kit,
4. Run machine learning molecular dynamics (ML/MD),
5. Use **active learning** together with **QbC** to adaptively improve the model,

Preparation
-----------

First, create a new test directory, and download tutorial data:

.. code-block:: bash

   mkdir nh3bh3_test
   cd nh3bh3_test
   wget https://github.com/rahulumrao/sparc/raw/main/examples/AmmoniaBorate.zip
   unzip AmmoniaBorate.zip

You can also download the archive directly from `here <https://github.com/rahulumrao/sparc/raw/main/examples/AmmoniaBorate.zip>`_ .

..   cp -r $SPARC_HOME/docs/tests/nh3bh3/* .   

If you `cd` to the folder it will have the following file,

.. code-block:: bash

   $ cd AmmoniaBorate
   $ ls
   INCAR  POSCAR  input.json  input.yaml  iter_000000  plumed_dp.dat
   $ tree iter_000000
      iter_000000
      └── 00.dft
         └── AseMD.traj

- ``POSCAR``: Initial structure in VASP format,
- ``INCAR``: VASP input file,
- ``plumed_dp.dat``: Plumed file,
- ``input.yaml``: SPARC input file,
- ``input.json``: DeepMD training parameters.

The file, ``AseMD.traj`` inside folder, ``iter_000000/00.dft`` the initial data to start the workflow computed from VASP. Now we only need to make ``yaml`` file for *sparc* configurations. To preapre input file see :ref:`inputfile` section.

The ``input.yaml`` defines the SPARC workflow, which is organized into four main steps:

1. Initial **Data preparation** with *ab initio* configurations
2. Run DeepMD-kit for **Training ML models**  interatomic potential models,
3. Use ASE MD engine together with Plumed to run **Machine Learning Molecular Dynamics (ML/MD)** sampling,
4. Iteratively improve ML potential with **Active learning** by detecting poorly represented regions with new candidates.


This loop enables SPARC to progressively refine the ML potential while maintaining high accuracy.

Running AIMD
------------

Run SPARC with the provided input:

.. code-block:: bash

   sparc -i input.yaml

This launches **iteration 0**:

.. code-block:: bash

   iter_000000/
   ├── 00.dft    # Ab initio MD data
   ├── 01.train  # Training of DeepMD models
   └── 02.dpmd   # ML-driven MD simulation

Training DeepMD
---------------

SPARC automatically collects AIMD data and prepares training/validation sets.
It then launches DeepMD training:

.. code-block:: bash

   cd iter_000000/01.train
   less lcurve.out

You should see a learning curve similar to:

.. image:: ../figures/learning_curve.png
   :width: 60%
   :align: center

Running ML/MD
-------------

Once models are trained, SPARC runs ML/MD simulations:

.. code-block:: bash

   cd iter_000000/02.dpmd
   ls

   AseTraj.xyz    # trajectory
   md.out         # log
   model_dev.out  # model deviation info

Monitoring Model Deviation
--------------------------

SPARC tracks force deviations between models:

.. code-block:: bash

   less model_dev.out

Frames with deviation above threshold are flagged and sent for relabeling
using VASP. These will appear in the **next iteration** folder.

Active Learning Loop
--------------------

The workflow continues automatically:

.. code-block:: bash

   iter_000001/
   ├── 00.dft
   ├── 01.train
   └── 02.dpmd

In each cycle:

1. Structures are labeled with DFT.
2. Models are retrained.
3. DPMD is run with updated potentials.

Analysis
--------

SPARC provides utilities for plotting and analysis. For example:

.. code-block:: python

   from sparc.src.utils.analysis_tools import plot_learning_curve
   plot_learning_curve("iter_000003/01.train/learning_curve.out")

Other available plots:

- Force deviation across iterations.
- Free energy surfaces (with PLUMED).
- Temperature/energy time series.

Enhanced Sampling
-----------------

SPARC integrates **PLUMED** for enhanced sampling:

- Metadynamics
- Umbrella sampling
- SPRINT collective variables

To enable, include a ``plumed_input`` key in ``input.yaml`` and provide
a ``plumed.dat`` file.

.. literalinclude:: plumed.dat
   :language: text
   :caption: Example ``plumed.dat`` for umbrella sampling.

Summary
-------

In this tutorial, we learned how to:

- Run AIMD with VASP inside SPARC.
- Train DeepMD potentials.
- Perform DPMD simulations.
- Use active learning to adaptively improve potentials.
- Couple simulations with PLUMED for rare-event sampling.

Next Steps
----------

- Try replacing the system with your own molecule or solid.
- Explore umbrella sampling with multiple windows.
- Use different collective variables (e.g. torsions, distances).
- Extend the workflow with NequIP or xTB calculators.

