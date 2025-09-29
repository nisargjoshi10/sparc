.. _quickstart:

Quick Start Guide
=================

Welcome to the Quick Start Guide for setting up and running your first simulation with ``SPARC``.  
This guide walks you through the basic setup, configuration, and execution steps, allowing you to quickly begin your calculations.  
Follow these steps to configure your environment and set up an input file.  
An example input file is provided in the `Basic Usage <BasicUsage>`_ section below.

Environment Variables:
----------------------

When using different *ab initio* packages, certain environment variables must be defined prior to executing the workflow. 
These ensure that the underlying electronic structure code can locate the required pseudopotentials, basis sets, and related data files.

- **First-principle Calculator**
  
  * **VASP**

    The pseudopotential library must be made available by setting the path to the POTCAR files through ``VASP_PP_PATH``.
    See the ASE `VASP documentation <https://ase-lib.org/ase/calculators/vasp.html>`_.

    .. code-block:: bash

      export VASP_PP_PATH=/path/to/vasp/potcar_files    # path to POTCAR files path

  * **CP2K**

    CP2K requires access to basis set and pseudopotential library, which is specified through the ``CP2K_DATA_DIR`` variable.
    See the ASE `CP2K documentation <https://ase-lib.org/ase/calculators/cp2k.html>`_.

    .. code-block:: bash

      export $CP2K_DATA_DIR=/path/to/cp2k/data        # path to CP2K basis set data directory

- **PLUMED**
  
  If PLUMED was installed manually (skip: if used ``conda-forge``), you need to set the ``plumed`` environment variable.

  .. code-block:: bash

    export PLUMED_KERNEL="$CONDA_PREFIX/lib/libplumedKernel.so"
    export PYTHONPATH="$CONDA_PREFIX/lib/plumed/python:$PYTHONPATH"

.. _BasicUsage:
Basic Usage
-----------

``SPARC`` code requires a ``YAML`` input file that specifies the essential parameters of the workflow.
Each block in the file controls different part of the workflow, such as system setup, MD settings, or the DFT calculator.  

An example input file is shown below.

Input File
----------

.. code-block:: yaml

    general:
      structure_file: "POSCAR"

    md_simulation:
      thermostat: "Nose"
      temperature: 300.0
      steps: 100
      timestep_fs: 1.0

    dft_calculator:
      name: "VASP"
      prec: "Normal"
      incar_file: "INCAR"
      exe_command: "mpirun -np 2 /path/to/vasp_std"

Running the WorkFlow
--------------------

Once the input file is configured, execute the workflow with command:

.. code-block:: bash

    sparc -i input.yaml

.. _quickstart_directory:
Directory Structure
-------------------

After the first iteration, SPARC creates the following directory structure:

.. code-block:: bash

  >>> Project Root
  ├── POSCAR
  ├── INCAR
  ├── input.json
  ├── input.yaml
  ├── Dataset
  │   ├── training_data
  │   └── validation_data
  ├── iter_000000
  │   ├── 00.dft
  │   ├── 01.train
  │   └── 02.dpmd
  ├── iter_000001
  │   ├── 00.dft
  │   ├── 01.train
  │   └── 02.dpmd

This layout organizes the outputs as follows:

  - **POSCAR /  INCAR**: Standard VASP structure and input file
  - **input.yaml**: User-defined configuration for SPARC execution.
  - **input.json**: Configuration DeePMD-kit ML training
  - ``Dataset``: Stores training and validation data for ML training
  - **iter_000000, iter_000001, ...**: Iteration folders containing:

    - ``00.dft``: First-principles calculation
    - ``01.train``: DeepMD-kit ML model training  
    - ``02.dpmd``: Molecular dynamics simulations with ML potential  

Each new iteration (e.g., ``iter_000001``, ``iter_000002``, ...) corresponds to an ``active learning cycle``,
in which the potential is refined with additional labelled data and retrained models.    

By default SPARC writes all log messages to an output file ``sparc.log``. A sample output file looks like this:

.. code-block:: bash

  ========================================================================
  BEGIN CALCULATION - 2025-04-08 22:30:32
  ========================================================================


          ######  ########     ###    ########   ######
          ##    ## ##     ##   ## ##   ##     ## ##    ##
          ##       ##     ##  ##   ##  ##     ## ##
          ######  ########  ##     ## ########  ##
                ## ##        ######### ##   ##   ##
          ##    ## ##        ##     ## ##    ##  ##    ##
          ######  ##        ##     ## ##     ##  ######
          --v0.1.0

  ========================================================================
  Creating directories for Iteration: 000000
  ========================================================================
  ├── iter_000000/
  │   ├── 00.dft/
  │   ├── 01.train/
  │   └── 02.dpmd/
  ========================================================================

  ! ab-initio MD Simulations will be performed at Temp.: 300K !

  ========================================================================

  ========================================================================
                    Starting AIMD Simulation [Langevin]
  ========================================================================
  Steps: 0, Epot: -23.900369, Ekin: 0.193890, Temp: 300.00
  Steps: 1, Epot: -23.868841, Ekin: 0.163737, Temp: 253.35
  Steps: 2, Epot: -23.809660, Ekin: 0.114040, Temp: 176.45
  Steps: 3, Epot: -23.785705, Ekin: 0.095163, Temp: 147.24
  ========================================================================
            DEEPMD WILL TRAIN 2 MODELS !
  ========================================================================

  ========================================================================
  RUNNING TRAINING IN FOLDER (iter_000000/01.train/training_1) !
  DeepMD Model Evaluation Results:
  ------------------------------------------------------------------------
  DEEPMD INFO    # ---------------output of dp test---------------
  DEEPMD INFO    # testing system : Dataset/validation_data
  DEEPMD INFO    # number of test data : 45
  DEEPMD INFO    Energy MAE         : 1.000640e+01 eV
  DEEPMD INFO    Energy RMSE        : 2.874460e+01 eV
  DEEPMD INFO    Energy MAE/Natoms  : 2.001280e+00 eV
  DEEPMD INFO    Energy RMSE/Natoms : 5.748920e+00 eV
  DEEPMD INFO    Force  MAE         : 7.150255e-02 eV/A
  DEEPMD INFO    Force  RMSE        : 9.012610e-02 eV/A
  DEEPMD INFO    Virial MAE         : 2.775489e-01 eV
  DEEPMD INFO    Virial RMSE        : 3.691740e-01 eV
  DEEPMD INFO    Virial MAE/Natoms  : 5.550977e-02 eV
  DEEPMD INFO    Virial RMSE/Natoms : 7.383479e-02 eV
  DEEPMD INFO    # -----------------------------------------------
  ========================================================================
  DeepPotential model successfully loaded and tested:
  iter_000000/01.train/training_1/frozen_model_1.pb
  ========================================================================

  ========================================================================
            Initializing DeepPotential MD Simulation [Langevin]
  ========================================================================
  Steps: 0, Epot: -29.804899, Ekin: 0.193890, Temp: 300.00
  Steps: 70, Epot: -29.761078, Ekin: 0.145811, Temp: 225.61
  Steps: 140, Epot: -29.791506, Ekin: 0.171109, Temp: 264.75
  Steps: 210, Epot: -29.771736, Ekin: 0.170868, Temp: 264.38
  Steps: 280, Epot: -29.755832, Ekin: 0.133304, Temp: 206.26
  Steps: 350, Epot: -29.801518, Ekin: 0.177911, Temp: 275.28
  Steps: 420, Epot: -29.736048, Ekin: 0.165758, Temp: 256.47
  Steps: 490, Epot: -29.717222, Ekin: 0.161525, Temp: 249.92
  ========================================================================

.. note::

   SPARC integrates three key components: molecular dynamics simulations,
   ML potential training, and active learning. For a more details, see
   :ref:`scientific_overview`.
