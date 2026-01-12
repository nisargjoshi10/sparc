.. .. role:: raw-math(raw)
..     :format: latex html

.. default-role:: math

Plumed Integtation
==================

.. module:: plumed_wrapper

Overview
--------

We used the open source `Plumed <plumed_>`_ library to accelerate the exploration of potential energy surface during MD simulations. This allows biasing of collective variables (CVs) to accelerate sampling of rare events, explore free energy landscapes, and perform advanced statistical simulations. The ASE build-in `plumed-wrapper <https://ase-lib.org/ase/calculators/plumed.html>`_ was attached with the existing calculator.


SPRINT Collective Variable
--------------------------

**SPRINT** (Social Permutation Invariant) is a global collective variable that provides a topology-based description of atomic connectivity, and is particularly useful in reactive simulations. Unlike geometrical CVs (eg: distance, angle, etc.) that are specific to a chemical reaction, **SPRINT** is a **global topological CV**.  

- It encodes the connectivity of the entire bonding network,  
- It detects bond rearrangements without requiring prior knowledge of configurational change,  
- It provides a single variable that responds automatically to changes anywhere in the system.  

This makes **SPRINT** particularly powerful for **constructing generalized machine learning potentials**:  

- If a potential is trained using CVs specific to one reaction, the ML model is biased toward only that pathway.  
- By contrast, using SPRINT ML/MD explores **all possible chemical tranformations** in the system.  
- This allows discovery of **unknown configurations and reaction channels** without manual input.  

In practice, biasing with **SPRINT** accelerates exploration of the potential energy surface (PES) as a whole, rather than a predefined reaction coordinate. This flexibility is critical when the aim is to build a **reactive ML potential** that must remain transferable across many chemical events. Once the **SPRINT** coordinate is set up, any self-guided enhanced sampling technique (e.g., `Metadynamics <https://www.plumed.org/doc-v2.9/user-doc/html/_m_e_t_a_d.html>`_ , `Parallel bias metadynamics <https://www.plumed.org/doc-v2.9/user-doc/html/_p_b_m_e_t_a_d.html>`_) can be applied to accelerate exploration of the PES. In this way, SPRINT provides a **general and reaction-independent CV** that drives efficient sampling while avoiding manual definition of chemical pathways.

..  together with Parellel Bias Metdynamics to accelerate the molecular dynamics simulation.

.. Once the **SPRINT** coordinate is setup any enhanced sampling techniques can be employed.

**SPRINT** coordinates are computed based on the equilibrium distances between atom types and the distances between 
each of the atoms in a system to construct a contact matrix. **SPRINT** is a generic coordinate based on 
the graph theory which has the universal discrimination of a chemical space. This allows the exploration of the potential energy space
much quicker. 

By definition **SPRINT** coordinate are calculated from the largest eiugenvalue, `\lambda` of an `n \times n` 
adjency matrix and its corresponding eigenvector, `\bf{V}`, using:

.. math::

   s_{i} = \sqrt{n} \lambda \mathit{v_i}

.. note::
    ``SPRINT`` coordinate is part of the ``adjmat`` module, therefore we need to compile Plumed with correct flag. 
    Please see the PLUMED section in the :ref:`InstalltionGuide`.

.. tip:: 
    Since the package incorporates PLUMED as an auxiliary calculator, 
    it enables the use of advanced enhanced sampling techniques to accelerate the exploration of the potential energy landscape. 
    We particularly recommend combining the ``SPRINT`` coordinates with `Parallel Bias Metadynamics (PBMetaD) <pbmetad>`_ ,
    as this approach offers efficient, self-guided exploration of complex chemical and configurational spaces.


API Reference
*************

.. .. autofunction:: sparc.src.plumed_wrapper.modify_forces

.. automodule:: sparc.src.plumed_wrapper
   :members: modify_forces
   :undoc-members:
   :show-inheritance:


The :func:`modify_forces` function provides the mechanism to wrap any ASE calculator with PLUMED:

- Reads the user-defined PLUMED input file (``plumed.dat``),  
- Returns the PLUMED-wrapped calculator ready for MD.  


Umbrella Sampling in SPARC
--------------------------

We implemented Umbrella sampling as a built-in capability of ``SPARC`` that can be employed for studying specific chemical reactions within an on-the-fly learning cycle. This allows free-energy landscapes of reactions to be mapped without relying entirely on expensive AIMD. The system is biased along a chosenset of collective variable, which allows only the reaction specific region of the potential energy surface to be sampled efficiently. As MD progresses, configurations encountered during the umbrella simulation can be labeled and added to the training set. The ML model is refined iteratively, ensuring that it remains accurate in the regions of phase space most relevant to the reaction of interest.

This means SPARC workflow can works both as a general framework for developing **generalized ML potentials** and as a practical tool for probing **targeted reaction studies**  in a cost-effective manner.

SPARC supports **umbrella sampling**, where a system is restrained in successive "windows" along a CV.  
Each window samples a different region of phase space, and the results are later combined (e.g., using WHAM or MBAR) to reconstruct the free energy profile.

YAML Settings for Umbrella Sampling
-----------------------------------

Enable PLUMED in the DeepMD section and point to an umbrella config file. The keys below are the minimal set typically needed for ML-MD umbrella runs.

.. code-block:: yaml

    # DeepMD training & MD settings (excerpt)
    deepmd_setup:
    use_plumed: True                        # <-- Enable PLUMED biasing during MD
    umbrella_sampling:
        enabled: True                         # <-- Turn on umbrella sampling
        config_file: "umbrella_sampling.yaml" # <-- Window list (see below)

``umbrella_sampling.yaml`` provides structure and a PLUMED file per window. Each window restrains the CV to a different mean position.

.. code-block:: yaml

    # umbrella_sampling.yaml
    umbrella_windows:
    - structure: "harmonic/POSCAR_4.0"
        plumed_file: "harmonic/plumed_w4.0.dat"
    - structure: "harmonic/POSCAR_3.9"
        plumed_file: "harmonic/plumed_w3.9.dat"
    - structure: "harmonic/POSCAR_3.8"
        plumed_file: "harmonic/plumed_w3.8.dat"
    - structure: "harmonic/POSCAR_3.7"
        plumed_file: "harmonic/plumed_w3.7.dat"


Folder Layout Example
---------------------

A typical setup for umbrella sampling with ``SPARC`` requires a ``umbrella_sampling.yaml`` file with window and structire defintions and a directory containing all the files similar to this,

.. code-block:: bash
    
    umbrella_sampling.yaml
    harmonic/
        POSCAR_1.4  POSCAR_1.5  ...  POSCAR_4.0
        plumed_w1.4.dat  plumed_w1.5.dat  ...  plumed_w4.0.dat

Each ``POSCAR_x.x`` defines the starting structure for that particlar window, and each ``plumed_wx.x.dat`` contains the corresponding restraint on the CV.

Example PLUMED File
-------------------

For umbrella sampling, each PLUMED file typically defines a CV, a harmonic restraint and mean position for that particular window.

**Conceptual example** (names are illustrative; use your actual CV syntax):

.. code-block:: bash
    
    $ cat plumed_3.2.dat
    
    # Units
    UNITS LENGTH=A ENERGY=kcal/mol
    
    # CV definitiona
    d1: DISTANCE ATOMS=1,4
    d2: DISTANCE ATOMS=2,1
    d3: DISTANCE ATOMS=3,2
    d4: DISTANCE ATOMS=4,3
    
    # Activate Umbrella Sampling in distance (butadiene)
    # with kapps equal to 1.5au/Ang^2 (941.26 kcal/mol/Ang^2), distance equal Angstrom
    # Haarmonic restrains
    rest: RESTRAINT ARG=d1 KAPPA=941.26 AT=3.2

    # Output
    FLUSH STRIDE=100
    PRINT ARG=d1,d2,d3,d4,rest.bias STRIDE=3 FILE=COLVAR

Output
------

When umbrella sampling is enabled:
- SPARC creates a **separate window folder run per window** (individual folders),
- Writes per-window logs and trajectories (e.g., ``usmd.log``, ``PLUMED.log``, ``dpmd.traj``, ``COLVAR``).


.. code-block:: yaml

         ######  ########     ###    ########   ######
        ##    ## ##     ##   ## ##   ##     ## ##    ##
        ##       ##     ##  ##   ##  ##     ## ##
         ######  ########  ##     ## ########  ##
              ## ##        ######### ##   ##   ##
        ##    ## ##        ##     ## ##    ##  ##    ##
         ######  ##        ##     ## ##     ##  ######
         --v0.1.0

    [SPARC][INFO] ========================================================================
        deepmd_setup:
        MdSimulation: true
        data_dir: DeePMD_training/00.data
        input_file: input.json
        log_frequency: 1
        md_steps: 2000
        multiple_run: 1
        num_models: 2
        skip_max: null
        skip_min: 0
        timestep_fs: 1.0
        training: false
        umbrella_sampling:
        config_file: umbrella_sampling.yaml
        enabled: true
        use_plumed: true
    [SPARC][INFO] YAML configuration loaded successfully!
    [SPARC][INFO] ========================================================================
    [SPARC][INFO] DeepPotential model successfully loaded and tested: iter_000000/01.train/training_1/frozen_model_1.pb
    [SPARC][INFO] Umbrella Sampling Enabled — Running MLMD Windows with PLUMED
    [SPARC][INFO] Running Umbrella Sampling for window 000
    [SPARC][INFO] → Window 000 | Structure: harmonic/POSCAR_4.0 | PLUMED: harmonic/plumed_w4.0.dat
    [SPARC][INFO] PLUMED output will be written to iter_000000/02.dpmd/window_000
    [SPARC][INFO] Initializing DeepPotential MD Simulation [Nose]
    [SPARC][INFO] Steps: 0,  Epot: -56.295802, Ekin: 0.387780, Temp: 300.00
    [SPARC][INFO] Steps: 1,  Epot: -56.297839, Ekin: 0.389817, Temp: 301.58
    [SPARC][INFO] Steps: 2,  Epot: -34.208572, Ekin: 0.392854, Temp: 303.93
    [SPARC][INFO] Running Umbrella Sampling for window 001
    [SPARC][INFO] → Window 001 | Structure: harmonic/POSCAR_3.9 | PLUMED: harmonic/plumed_w3.9.dat
    [SPARC][INFO] PLUMED output will be written to iter_000000/02.dpmd/window_001
    [SPARC][INFO] Initializing DeepPotential MD Simulation [Nose]
    [SPARC][INFO] Steps: 0,  Epot: -56.479785, Ekin: 0.387780, Temp: 300.00
    [SPARC][INFO] Steps: 1,  Epot: -56.486391, Ekin: 0.394380, Temp: 305.11
    [SPARC][INFO] Steps: 2,  Epot: -56.493072, Ekin: 0.401053, Temp: 310.27

**Post-processing**  
    - After all windows finish, histograms are combined using `WHAM <http://membrane.urmc.rochester.edu/sites/default/files/wham/doc.pdf>`_/`MBAR <https://fastmbar.readthedocs.io/en/latest/>`_ to recover the unbiased free energy surface.

API Reference
*************

.. autofunction:: sparc.src.plumed_wrapper.umbrella

.. Function:
.. ~~~~~~~~~

.. .. autofunction:: sparc.src.plumed_wrapper.modify_forces

.. API Reference
.. -------------

.. .. automodule:: sparc.src.plumed_wrapper
..    :members:
..    :undoc-members:
..    :show-inheritance:



References
~~~~~~~~~~

- Torrie, G. M. & Valleau, J. P. *Monte Carlo free energy estimates using non-Boltzmann sampling: Application to the sub-critical Lennard-Jones fluid.* Chem. Phys. Lett. **28**, 578-581 (1974).  
- Pfaendtner, J. & Bonomi, M. *Efficient sampling of high-dimensional free energy landscapes with Parallel Bias Metadynamics.* J. Chem. Theory Comput. **11**, 5062-5067 (2015).
- Pietrucci, F., & Andreoni, W. *Graph Theory Meets Ab Initio Molecular Dynamics: Atomic Structures and Transformations at the Nanoscale*. Phys. Rev. Lett., 107(8), 085504 (2011). 
- PLUMED documentation: https://www.plumed.org/doc-v2.9/user-doc/html/_s_p_r_i_n_t.html  


.. _plumed: https://www.plumed.org/
.. _asePlumed: https://ase-lib.org/ase/calculators/plumed.html
.. _pbmetad:: https://www.plumed.org/doc-v2.9/user-doc/html/_p_b_m_e_t_a_d.html
.. _sprint: http://dx.doi.org/10.1103/PhysRevLett.107.085504