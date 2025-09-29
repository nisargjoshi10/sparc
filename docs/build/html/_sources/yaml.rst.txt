.. _inputfile:
Input File
==========

The SPARC input is organized into several sections, and each section controls different task in the workflow. Every section contains required key-value pairs as well as optional parameters that can be defined by the user.

Because each section is independent, tasks such as ``*ab initio* calculations``, ``MLP training``, ``ML molecular dynamics``, or ``active learning`` can be executed separately or together.  

The required and optional keywords for each section are described below.

General Settings
~~~~~~~~~~~~~~~~

This section requires the coordinate structure file to begin the calculation.
.. Currently only ``POSCAR`` file format is supported.

.. code-block:: yaml

    # General settings
    general:
      structure_file: "POSCAR"  # Input structure [Default]

DFT Calculator
--------------

Here, we define the parameters for the DFT calculator (e.g., VASP), and the executable command path.
For flexibilty, it is also possible to directly parse the ``INCAR`` file.

.. code-block:: yaml

    # DFT calculator settings
    dft_calculator:
      name: "VASP"               # DFT package name         [Required]
      prec: "Normal"             # Precision level          [Required]
      kgamma: True               # Gamma point calculation  [Required]
      incar_file: "INCAR"        # Path to INCAR file       [Required]
      exe_command: "mpirun -np 2 /path/to/VASP/bin/vasp_std"  # Full command to run VASP with MPI [Required]

.. note::
  
  Refer to the :ref:`calculator` page for the instructions on configuring alternate DFT calculator (e.g., CP2K) setup.

MD Simulation
-------------

This section configures the molecular dynamics (MD) simulation settings, including the type of thermostat (Nose-Hoover or Langevin), the number of MD steps, and the timestep, etc.

.. code-block:: yaml

    # ASE MD simulation settings
    md_simulation:
      ensemble: "NVT"           # Ensemble for MD simulation                  [Required]
      thermostat:               # Thermostat configuration as a dictionary    [Required]
        type: "Nose"            # Thermostat type (Nose-Hoover or Langevin)   [Required]
        tdamp: 10.0             # Damping parameter for Nose-Hoover thermostat [Required]
      timestep_fs: 1.0          # TimeStep for MD simulation                   [Optional (Default: 1.0)]
      temperature: 300          # Temperature in Kelvin                        [Optional (Default: 300)]
      steps: 10                 # Number of AIMD steps                         [Required]
      restart: False            # Restart AIMD simulation from checkpoint file [Optional (Default: False)]
      use_dft_plumed: True      # Use PLUMED for AIMD simulation               [Optional (Default: False)]

- Check out :ref:`aimdplumed` section for running AIMD together with PLUMED.
  
.. note::

    Both the ``Nose-Hoover`` and ``Langevin`` thermostats are available.

    - If ``Nose`` thermostat, the ``tdamp`` parameter must be specified.
    - If ``Langevin`` thermostat is chosen, the ``friction`` parameter must be specified. 

    For further details, refer to the `Molecular Dynamics <asemd_>`_ section in ASE.

    .. code-block:: yaml

      type: Nose
      tdamp: 0.01

      type: Langevin
      friction: 0.01

.. _aimdplumed:
PLUMED
------

This section controls the settings of PLUMED plugin for AIMD simulations. It requires a input file name, and the thermal energy parameter ``kT`` (in eV).

.. code-block:: yaml

    # Plumed settings
    dft_plumed:
      input_file: "plumed_dft.dat"  # PLUMED input file
      restart: False                # Restart PLUMED        [Optional (Default: False)]
      kT: 0.02585                   # kT value [eV] units   [if Plumed=True[Required]]

.. _deepmd_section:
DeepMD
------

This section defines the settings for training a DeepMD model. 
It includes the paths to the training data and input files, as well as the number of models to generate.

.. code-block:: yaml

    # DeepMD settings
    deepmd_setup:
      training: False           # Enable DeepPotential training  [Required]
      data_dir: "DeePMD_training/00.data"  # Path to store training and validation data [Optional]
      input_file: "input.json"  # Input file for DeepMD training  [Required]
      skip_min: 0               # Minimum frames to skip  [Optional] exclude 
      skip_max: null            # Maximum frames to skip  [Optional]
      num_models: 2             # Number of models to be trained  [Required (can not be less than 2)]
      MdSimulation: True        # DeepPotential MD simulation (False/True)  [Required]
      timestep_fs: 1.0          # Timestep (fs) [Optional (Default: 1.0)]
      md_steps: 2000            # MLP-MD steps  [Required]
      multiple_run: 5           # Run multiple MD-MLP run starting from different velocities [Optional (Default: 0)]
      log_frequency: 5          # Output frequency  [Required]
      use_plumed: True          # Default: False  [Optional]
      plumed_file: "plumed.dat" # Optional: defaults to "plumed.dat" if not specified


Active Learning
---------------

Active learning is enabled by setting the flag to ``True``. This section defines how the workflow loop is executed, including the number of iterations and the force deviation thresholds. The workflow can be restarted by setting ``learning_restart`` to ``True``, which also requires the path to the ``latest_model``.

.. code-block:: yaml

    # Active Learning
    active_learning: False      # [Required (Default: False)]
    learning_restart: False     # Restart AL loop from last step  [Optional]
    latest_model: 'iter_000006/01.train/training_1/frozen_model_1.pb'   # Latest Model path to restart [Required (if above True)]
    iteration: 10               # Active Learning iteration steps [Optional (default: 10)]
    model_dev:
      f_min_dev: 0.1            # [Required]
      f_max_dev: 0.8            # [Required]


Metric
------

The ``metric`` section provides sanity checks to avoid unphysical structures or unstable trajectories during ML/MD simulation. Since an initial ML potential may not have sufficient information about the potential energy surface. This will stop the code to run indefinetly and move to next iteration. 

Currently, two types of metrics are supported:

1. **Distance Metric**
  Define minimum and maximum bond distances between atom pairs. If a distance falls outside the specified range, the MD simulation is stopped and the workflow proceeds to the next iteration.

.. code-block:: yaml

    # check metrics [Optional]
    distance_metrics:
      - pair: [0, 3]
        min_distance: 1.2  # Minimum allowed distance in Angstroms
        max_distance: 5.0  # Maximum allowed distance in Angstroms
      - pair: [0, 1]
        min_distance: 1.2  # Minimum allowed distance in Angstroms
        max_distance: 2.0  # Maximum allowed distance in Angstroms
    # If you want to skip distance checks, you can comment out or remove this section.

2. **Energy Metric**  
  Monitor the potential energy relative to a reference (taken from the first MD step).  
  If the energy deviates beyond a user-defined threshold, the simulation is stopped.  
  This prevents the system from exploring unphysical regions of the potential energy surface.

  .. code-block:: yaml

      # Energy check [Default]
      deepmd_setup:
        epot_threshold: 5.0    # Maximum allowed deviation energy (in eV)

  In this case, if the potential energy exceeds the allowed range, MD simulation will be terminated and the error will be logged. The workflow will then proceed to the next iteration.

.. math::

  E_\text{pot} < E_\text{ref} - \Delta E
  \quad \text{or} \quad
  E_\text{pot} > E_\text{ref} + \Delta E

where:

- :math:`E_\text{ref}` is the reference energy at the first MD step,
- :math:`E_\text{pot}` is the current potential energy,
- :math:`\Delta E` is the user-defined threshold. (``epot_threshold``)

.. note::

  - Both distance and energy checks are **optional** but recommended when starting with less training data.
  - If you wish to disable them, simply comment out or remove the corresponding section.

Output
------

Each iteration produces several output files. The filenames shown are defaults but may be overridden by the user.

.. code-block:: yaml

    # File output settings
    output:
      log_file: "AseMD.log"        # Log file of MD simulation        [Optional (Default: AseMD.log)]
      aimdtraj_file: "AseMD.traj"  # ASE trajectory file for AIMD run [Optional (Default: AseMD.traj)]
      dptraj_file: "dpmd.traj"     # ASE DeepMD trajectory file       [Optional (Default: dpmd.traj)]


``log_file`` contains the MD information, and ``traj`` file stores the trajectory structures.

.. code-block:: bash
  
  Time[ps]      Etot[eV]     Epot[eV]     Ekin[eV]    T[K]
  0.0000        -112.0807    -112.8950       0.8143   300.0
  0.0700        -111.6322    -112.7149       1.0828   398.9
  0.1400        -112.4215    -113.3518       0.9303   342.7
  0.2100        -112.9996    -113.6775       0.6779   249.8
  0.2800        -112.6910    -113.7220       1.0310   379.8

Directory structure
-------------------

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

For detailed output see section :ref:`quickstart_directory`.

A template input file is available at `scripts <https://github.com/rahulumrao/sparc/blob/main/scripts/input.yaml>`_ folder, for all the settings of ``SPARC``.

.. _asemd: https://wiki.fysik.dtu.dk/ase/tutorials/md/md.html