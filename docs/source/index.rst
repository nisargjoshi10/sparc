.. SPARC documentation master file, created by
   sphinx-quickstart on Tue Mar 25 19:57:53 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. raw:: html

   <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 20px;">
      <img src="_static/sparc_logo.png" alt="SPARC Logo" style="height: 150px; object-fit: contain;">
      <span style="font-size: 1.5em; font-weight: bold;">Welcome to SPARC's documentation!</span>
   </div>


.. Welcome to SPARC's documentation!
.. =================================

**SPARC** (**S**\ mart **P**\ otential with **A**\ tomistic **R**\ are Events and **C**\ ontinuous Learning) :is a Python package built around the `ASE <ase_>`_ library. 
``SPARC`` is a modular workflow for training machine learning interatomic potentials (MLIPs) for reactive/nonreactive system. 
It supports various first-principle calculators, and ML arcitechture together with accelerated sampling of configurational space, which enables efficient simulation and on-the-fly model improvement.

.. _scientific_overview:

Scientific Overview
--------------------
Constructing a reactive and transfarable ML potential is challanging, as it requires high quality training data which includes rare events, high energy intermediates, and transition state.
A ML model that can generate chemically accurate potential energy surface is important for studying rare events.
SPARC automates this by pushing a trained ML model to access different configurations in the potential energy surface to predict beyond its knowledge.
The idea behind SPARC is to use the active learning protocol together with advance sampling techniques that systematicallt identifies new configurations and trains a ML model on-the-fly.
the workflow consist of four main steps, three main steps, ML model training using `DeePMD-kit <deepmd_>`_ package, accelerated sampling driven PES exploration using `PLUMED <plumed_>`_ library, 
and new configuration labelling using first-principle calculations, which are executed iteratively in a loop until a reactive and stable MLIP is constructed. .

.. toctree::
   :maxdepth: 2
   :caption: Getting Started:

   install.rst
   quickstart
   yaml
   calculator
   deepmd
   md
   DataProcess
   plumed_wrapper
   tutorial
   analysis
   workflow
   user_guide/index
   api/index
   tests/index
   contributing

Key Features
------------
SPARC provides the following core functionalities:

- **First-principles calculations** and *ab inito* molecular dynamis simulation together with PLUMED plugin.
- **Machine-learning potential training** with `DeepMD-kit <deepmd_>`_.
- **Machine-learning molecular dynamics (ML/MD)** simulations using `ASE MD <asemd_>`_ engine for NVT ensamble.
- **Active learning** using query-by-committee approach to label new configurations for continuous model improvement.
- **Potential energy surface exploration** with integration of `PLUMED <plumed_>`_ plugin.
- **Visualisation** of verious properties to monitor the workflow.

Use Cases
---------
Here are some example use cases for SPARC:

1. **Material property prediction:** : Develop accurate interatomic potentials for materials property prediction and molecular dynamics simulation.
2. **Chemical reaction pathways:** : Uncover reaction mechanisms by finding new configurations and training a ML model on-the-fly.
3. **High-throughput simulations:** to efficiently explore large chemical spaces.

Installation
------------
For detailed installation instructions, please refer to the `Installation Guide <install.html>`_.

Indices and Tables
******************

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search` 
  
.. _vasp: https://www.vasp.at/
.. _deepmd: https://github.com/deepmodeling/deepmd-kit
.. _plumed: https://www.plumed.org/
.. _ase: https://wiki.fysik.dtu.dk/ase/
.. _asemd: https://ase-lib.org/ase/md.html