.. _InstalltionGuide:
SPARC Installation Guide
========================

This guide provides step-by-step instructions to install SPARC. Currently SPARC supports DeePMD-kit version 2.2.10 for ML arcitechture, however with the next version we plan to also support DeePMD-kit 3.

After the installation, ``sparc`` will be available to execute.

.. Quick Start
.. -----------

.. For experienced users, the basic setup steps are:

.. .. code-block:: bash

..    conda create -n sparc python=3.10
..    conda activate sparc
..    pip install deepmd-kit[gpu,cu12,lmp]
..    git clone https://github.com/rahulumrao/sparc.git && cd sparc
..    pip install .


Dependencies:
-------------

.. _tbl-grid:

+--------------+-------------+
| Core Software Dependencies |
+==============+=============+
| Python       | >= 3.9      |
+--------------+-------------+
| DeepMD-kit   | 2.2.10      |
+--------------+-------------+
| ASE          | 3.24.0      |
+--------------+-------------+
| VASP/CP2K    |             |
+--------------+-------------+
| PLUMED       |             |
+--------------+-------------+


Python Package Dependencies:
----------------------------

* numpy
* pandas
* dpdata

.. note::

   Assuming `Anaconda <https://anaconda.org/>`_ is already installed in the Linux environment. If not then follow the `instructions <https://www.anaconda.com/docs/getting-started/anaconda/install>`_ here.


Step-by-Step Installation
-------------------------

1. Create and activate a conda environment:

   .. code-block:: bash

      conda create -n sparc python=3.10
      conda activate sparc

2. Use any of the following methods to install `DeepMD-kit <dpmd_install_>`_ :

- conda

   .. code-block:: bash

      conda install deepmd-kit=2.2.10=*gpu libdeepmd=2.2.10=*gpu lammps horovod -c https://conda.deepmodeling.com -c defaults

- pip

   .. code-block:: bash

      pip install deepmd-kit[gpu,cu12]==2.2.10

.. important:: 

   Deepmd-kit ``pip install tensorflow[and-cuda]`` may not always detect the GPU due to potential configuration issues.
   To verify if TensorFlow has successfully recognized the GPU, execute the following command,
   
   .. code-block:: bash

      (sparc):~$ python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
      (sparc):~$ [PhysicalDevice(name='/physical_device:GPU:0', device_type='GPU'), PhysicalDevice(name='/physical_device:GPU:1', device_type='GPU')]
   
   If the output is an empty list,

   .. code-block:: bash

      (sparc):~$ Skipping registering GPU devices... 
      (sparc):~$ []
   
   Check,

   - NVIDIA driver and CUDA toolkit installation
   - CUDA version compatibility with TensorFlow
   - Linux environment variables (e.g., `LD_LIBRARY_PATH`) are correctly set
   
   Also, refer to the `TensorFlow GPU troubleshooting guide <tf_>`_ for details.

   Some hardware have also shown issues with ``conda`` channels:
   
   .. code-block:: bash
      
      LibMambaUnsatisfiableError: Encountered problems while solving:
      nothing provides __cuda needed by libdeepmd-2.2.10-0_cuda10.2_gpu
      nothing provides __cuda needed by tensorflow-2.9.0-cuda102py310h7cc18f4_0
      Could not solve for environment specs
      The following packages are incompatible
      ├─ deepmd-kit 2.2.10 *gpu is not installable because it requires
      │  └─ tensorflow 2.9.* cuda*, which requires
      │     └─ __cuda, which is missing on the system;
      └─ libdeepmd 2.2.10 *gpu is not installable because it requires
      └─ __cuda, which is missing on the system.


3. Clone and install SPARC:

   .. code-block:: bash

      git clone https://github.com/rahulumrao/sparc.git
      cd sparc
      pip install .
      
.. _InstallPlumed:
4. Install PLUMED:

   .. code-block:: bash

      conda install -c conda-forge py-plumed

.. note::
   Some Collective Variables (CVs), such as Generic CVs (e.g., ``SPRINT``), are part of the additional module and are not included in a standard PLUMED installation. 
   To enable them, we need to manually install PLUMED and wrap with Python.

   Download the `PLUMED package <https://www.plumed.org/download>`_ from the official website.
   During installation, PLUMED will detect the Python interpreter from the active ``conda environment`` and enable Python bindings.

   .. code-block:: bash

      ./configure --enable-mpi=no --enable-modules=all PYTHON_BIN=$(which python) --prefix=$CONDA_PREFIX
      
      make -j$(nproc) && make install

   Once the installation is complete, a directory named ``plumed`` inside the ``lib`` folder inside ``conda environment``.

   To verify the installation, run the following command in the terminal:

   .. code-block:: python

      >>> ls /home/user/anaconda3/envs/sparc/lib/plumed

   Expected output:

   .. code-block:: ini

      fortran     patches        plumed-mklib  plumed-partial_tempering  plumed-runtime   plumed-vim2html  src
      modulefile  plumed-config  plumed-newcv  plumed-patch              plumed-selector  scripts          vim

   You can also import the module in Python to confirm installation:

   .. code-block:: python

      >>> from ase.calculators.plumed import Plumed
      >>> help(Plumed)
         Help on class Plumed in module ase.calculators.plumed:
         class Plumed(ase.calculators.calculator.Calculator)
         |  Plumed(calc, input, timestep, atoms=None, kT=1.0, log='', restart=False, use_charge=False, update_charge=False)
         |
         |  Method resolution order:
         |      Plumed
         |      ase.calculators.calculator.Calculator
         |      ase.calculators.calculator.BaseCalculator
         |      ase.calculators.abc.GetPropertiesMixin


Verification
------------

Once installed with all dependencies, the command-line execution will prints:

.. code-block:: bash

   >>> sparc -h
      
      sparc [-h] [-i INPUT_FILE]

      options:
      -h, --help            show this help message and exit
      -i INPUT_FILE, --input_file INPUT_FILE
                              Input YAML file

.. warning:: 
   This package is under active development, therefore some features and APIs may change.
   Also, this workflow is designed to work in a Linux environment. It may not be fully compatible with macOS systems.



.. _dpmd_install: https://docs.deepmodeling.com/projects/deepmd/en/stable/getting-started/install.html
.. _plumed: https://www.plumed.org/download
.. _tf: https://www.tensorflow.org/install/pip