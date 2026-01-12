.. _workflow_analysis:

Simulation Monitoring & Analysis
================================

Overview
--------
SPARC provides interactive modules for **workflow inspection** and **analysis** of active learning iterations.  
These tools allow monitoring of energetic/geometric properties from MD trajectories, as well as model reliability indicators (e.g., learning curves, force deviation, uncertainty).

The utilities are designed for **Jupyter Notebook environments**, integrating ``ipywidgets``, ``matplotlib``, and ``ASE``.

--------------------
Workflow Analysis
--------------------

The workflow interface provides an interactive way to inspect outputs across multiple iterations, particularly useful for visualizing energetics and geometrical trends during training.

Features
~~~~~~~~
- Load and visualize per-iteration properties (temperature, energy, etc.) from trajectory files.
- Interactive widgets for selecting root directory, subfolder, trajectory, and iterations.
- Geometry analysis tab for plotting **bond lengths** or **angles** with user-defined indices.

Dependencies
~~~~~~~~~~~~
- numpy  
- matplotlib  
- ASE (Atomic Simulation Environment)  

Quick Start
~~~~~~~~~~~
1. Launch a Jupyter Notebook.
2. Import and run the workflow interface:

.. code-block:: python

    from sparc.src.utils.workflow import WorkFlowAnalysis
    WorkFlowAnalysis()

3. The interface will appear with tabs for:
   - Temperature
   - Total Energy
   - Potential Energy
   - Kinetic Energy
   - Geometry (Bond / Angle)

4. For each tab:
   - Set the root directory containing ``iter_xxxxxx`` folders.
   - Specify subfolder (default: ``02.dpmd``) and trajectory file (default: ``dpmd.traj``).
   - Click *Refresh Iterations* to detect available folders.
   - Select iterations and generate plots.

Example Directory Layout
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    project_root/
    ├── iter_000000/
    │   └── 02.dpmd/
    │       └── dpmd.traj
    ├── iter_000001/
    │   └── 02.dpmd/
    │       └── dpmd.traj
    └── iter_000002/
        └── 02.dpmd/
            └── dpmd.traj

Geometry Tab
~~~~~~~~~~~~
- Choose "Bond" or "Angle" type.
- Provide atom indices (e.g., ``0 1`` or ``0 1 2``).
- The y-axis will render the proper chemical symbols with subscripts.

Workflow
~~~~~~~~

.. automodule:: sparc.src.utils.workflow
    :members: WorkFlowAnalysis   

.. image:: ../_static/WorkflowAnalysis.gif
    :alt: Workflow Analysis Animation
    :width: 600px

--------------------
Advanced Analysis
--------------------

Monitoring the training progress of the ML potential requires systematic evaluation of learning and predictive reliability.  
SPARC provides modules for analyzing **physical** and **statistical** indicators:

- **Learning curves**: energy/force loss evolution.  
- **Parity plots**: comparison of predicted vs reference quantities.  
- **Uncertainty metrics**: ensemble variance, deviation in forces.  
- **Physical observables**: trajectory-based properties (temperature fluctuations).

..    density, RDF, etc.).  

Model Deviation in Forces
~~~~~~~~~~~~~~~~~~~~~~~~~
The **model deviation** metric quantifies how much an ensemble of models disagree on predicted forces.  
Large deviations signal regions of phase space where the model is uncertain and more training data is required.

Mathematical Definition:

.. math::

    \epsilon_{\mathbf{F}, i}(\mathbf{x}) = \sqrt{ \frac{1}{n_m} \sum_{k=1}^{n_m} \left\| \mathbf{F}_i^{(k)} - \bar{\mathbf{F}}_i \right\|^2 }

where:

- :math:`\mathbf{F}_i^{(k)}` = force on atom :math:`i` from model :math:`k`  
- :math:`\bar{\mathbf{F}}_i = \frac{1}{n_m} \sum_{k=1}^{n_m} \mathbf{F}_i^{(k)}` = ensemble average force  
- :math:`n_m` = number of models in the ensemble  
- :math:`\|\cdot\|` = Euclidean norm  

.. **In practice:**

.. 1. Predict forces using multiple models.  
.. 2. Compute the ensemble average.  
.. 3. Measure deviations from the average.  
.. 4. Take RMS of deviations.  

.. This serves as a **proxy for uncertainty**.

.. _modeldevi: https://docs.deepmodeling.com/projects/deepmd/en/master/test/model-deviation.html

.. image:: images/model_devi.jpg
    :alt: Visualization of force model deviation
    :align: center
    :width: 700px
    :target: ../_static/model_devi.jpg


--------------------
Example Notebooks
--------------------

.. toctree::
    :maxdepth: 1

    notebooks/analysisAmmoniaBorate.ipynb

--------------------
API References
--------------------

.. .. autofunction:: sparc.src.utils.plot_utils.PlotForceDeviation

.. .. automodule:: sparc.src.utils.plot_utils
..     :members: PlotForceDeviation, PlotLcurve, PlotPotentialEnergy, PlotDistribution, PlotPES, PlotTemp, ViewTraj

.. automodule:: sparc.src.utils.plot_utils
  :members: PlotForceDeviation, PlotLcurve, PlotPotentialEnergy, PlotDistribution, PlotPES, PlotTemp, ViewTraj
  :exclude-members:
  :undoc-members:
  :show-inheritance:       

