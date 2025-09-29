.. _calculator:

DFT Calculator
==============

.. Overview
.. --------

We have implemented both ``VASP`` and ``CP2K`` for first principle calculaton. In future we planned to additional calculators. 
Most of the settings inside ``dft_calculator`` section are default and will work as it is. However for both the calculators an additional input file is required which native to the calculator user has chosen.
This might seems redundant however, it provides more fexibilty to the users of choosing their own template for any system of choice.

For ``VASP`` user can parse thier own ``INCAR`` file with all the input keywords native to ``VASP``. See more in ASE `VASP documentaition <https://ase-lib.org/ase/calculators/vasp.html>`_

Class : SetupDFTCalculator
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. set up DFT calculators for VASP and CP2K.

.. function
.. ********

VASP
----

.. code-block:: yaml

  # DFT calculator settings
  dft_calculator:
    name: "VASP"               # DFT package name
    prec: "Normal"             # Precision level
    kgamma: True               # Gamma point calculation
    incar_file: "INCAR"        # Path to INCAR file
    exe_command: "/path/to/VASP/bin/vasp_std"  # Full command to run VASP with MPI

A minimal ``INCAR`` is given below,

.. code-block:: bash

    # Global Parameters #
    SYSTEM = AmmoniaBorate
    ISTART = 0
    ICHARG = 2
    ISPIN  = 1
    ENCUT  = 300
    LCHARG = .FALSE.
    LWAVE  = .FALSE.
    # Electronic Relaxation #
    ISMEAR = 0
    SIGMA  = 0.05
    EDIFF  = 1E-05


CP2K
----

.. code-block:: yaml

    # CP2K calculator 
    dft_calculator:
        name: "CP2K" # DFT package name
        template_file: "cp2k_template.inp" # Path to INCAR file
        exe_command: "mpirun -np 2 /path/to/cp2k/exe/local/cp2k_shell.psmp"

A minimal ``CP2K`` input template file (``cp2k_template.inp``) is given below,

.. code-block:: ini

  ! This is a comment
  # This is a comment
  &GLOBAL
  ECHO_INPUT
  &END GLOBAL
  &FORCE_EVAL
  &DFT
      CHARGE 0
      MULTIPLICITY 1
  &MGRID
      REL_CUTOFF 25
      NGRIDS 3
  &END MGRID
  &QS
      METHOD GPW #GAPW
      EPS_DEFAULT 1.0E-12
      EPS_PGF_ORB 1.0E-14
      EXTRAPOLATION ASPC
      EXTRAPOLATION_ORDER 3
  &END QS

  &SCF
    EPS_SCF 1.0E-4
    &OT
      PRECONDITIONER FULL_ALL
    &END
    &OUTER_SCF
      EPS_SCF 1.0E-4
      MAX_SCF 3
    &END
    SCF_GUESS RESTART
  &END SCF
  &END DFT

  &SUBSYS
      &KIND B
        ELEMENT O
      &END KIND
      &KIND H
        ELEMENT H
      &END KIND
      &KIND N
        ELEMENT N
      &END KIND
  &END SUBSYS
  &END FORCE_EVAL


.. note:: 
    Ensure that the executable path is correctly specified in ``exe_command`` key inside the ``yaml`` file.


.. automodule:: sparc.src.calculator
  :members: SetupDFTCalculator, dft_calculator
  :exclude-members: orca, xtb
  :undoc-members:
  :show-inheritance:


Example Use:
------------

.. code-block:: python

  import os
  from ase import Atoms
  from ase.io import read, write
  from sparc.src.calculator import dft_calculator

  # VASP input file
  incar = """
  # Global Parameters #
  SYSTEM = Water
  ISTART = 0
  ICHARG = 2
  ISPIN  = 1
  ENCUT  = 300
  LCHARG = .FALSE.
  LWAVE  = .FALSE.
  # Electronic Relaxation #
  ISMEAR = 0
  SIGMA  = 0.05
  EDIFF  = 1E-05
  """
  # save file in INCAR format
  with open("INCAR", 'w') as file:
      file.write(incar)
    
  # required configuration setup
  config = {
      "dft_calculator": {
          "name": "VASP",
          "prec": "Normal",
          "kgamma": True,
          "incar_file": "INCAR",
          "exe_command": "/path/to/VASP/bin/vasp_std",
      }
  }

  # Structure
  atoms = Atoms('H2O')
  atoms.set_cell([8.0, 8.0, 8.0])
  atoms.set_pbc([True, True, True])
  print (atoms)

  # Build calculator and attach to atoms object
  calc = dft_calculator(config, print_screen=True)
  atoms.calc = calc
  print("VASP energy (eV):", atoms.get_potential_energy())

output:

.. code-block:: text

    Atoms(symbols='H2O', pbc=True, cell=[8.0, 8.0, 8.0])
    [SPARC][INFO] ==================================================
    [SPARC][INFO]               INCAR PARAMETERS                
    [SPARC][INFO] ==================================================
    [SPARC][INFO]   SYSTEM : Water
    [SPARC][INFO]   ISTART : 0
    [SPARC][INFO]   ICHARG : 2
    [SPARC][INFO]   ISPIN  : 1
    [SPARC][INFO]   ENCUT  : 300.0
    [SPARC][INFO]   LCHARG : False
    [SPARC][INFO]   LWAVE  : False
    [SPARC][INFO]   ISMEAR : 0
    [SPARC][INFO]   SIGMA  : 0.05
    [SPARC][INFO]   EDIFF  : 1e-05
    [SPARC][INFO] ==================================================

    VASP energy (eV): -400.43427628