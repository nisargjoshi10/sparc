.. _deepmd:

DeePMD
======

For training deepmd model a working DeepMD-kit installation (``dp`` CLI available in ``$PATH``, see :ref:`InstalltionGuide`), and an input ``json`` file (``input.json``) compatible with DeepMD package is required.

Within each ``iter_xxxx`` directory, a ``01.train`` folder is created. Foe each model specidifed by ``num_models``, a subdirectory named ``training_n`` is created, where the training is executed. The training configurations is taken from the user defined ``input_file``, see :ref:`deepmd_section` section for details.


SPARC edits the base ``input.json`` for each model so that training data path remains same across each model, while assigns a **unique** `seed` value for each training. The following fields in the training configuration will be updated,

- Replace ``seed`` everywhere with a random value for each run,
- Set ``type_map`` for system specific ``atom_types``,
- Set ``training_data.systems = [ "<datadir>/training_data" ]``,
- Set ``validation_data.systems = [ "<datadir>/validation_data" ]``.

.. code-block:: json

   "model": {
      "type_map": ["O", "H"]

   "training": {
      "seed": 123456,
      "training_data": {
         "systems": []
      },
      "validation_data": {
         "systems": []
      },
      }


Logs are written to ``deepmd_training.log``. If more than four models are requested, a warning is logged. The function ``evaluate_model_accuracy`` evaluates each frozen model at the end of its training run.

.. tip::

   Train multiple models to improve accuracy.

After training each ``iter_xxxx/01.train/training_n`` should have a file ``frozen_model_n.pb`` file. 
These models are then used in a *Query-by-committee* approach to find new candidates for labelling.

.. note::
   **Query by committee (QbC)**: Identifies the configurations by measuring the disagreement among an ensemble of model. Allows the model to learn only **what it needs to** without wasting resources on redundant data. 
   See also Deepmd-kit `model deviation <qbc_>`_ for more details. 


If the candidates are found, a subdirecoty ``dft_candidates`` is created under the ``02.dft`` folder. It contains one ``POSCAR`` for each candidates.

.. code-block:: bash

   >>> tree dft_candidates
       ├── 0001
       │   └── POSCAR
       ├── 0002
       │   └── POSCAR
       ├── 0003
       │   └── POSCAR
       ├── 0004
       │   └── POSCAR
       ├── 0005
           └── POSCAR

.. (# change the path to sparc.src.deepmd later)
.. automodule:: sparc.src.deepmd
   :members: setup_DeepPotential
   :exclude-members: 
   :undoc-members:
   :show-inheritance:

.. code-block:: python

   from sparc.src.deepmd import setup_DeepPotential
   from ase import Atoms

   atoms = Atoms("H2O")
   system, calc = setup_DeepPotential(atoms, model_path='iter_000000/01.train/training_1', model_name='frozen_model_1.pb')
   print(system.get_potential_energy())


Returns ASE ``Atoms`` with DeepPotential calculator attached and corresponding ``deepmd.calculator.DP`` instance.


Example: Evaluate a Frozen Model
--------------------------------

.. code-block:: python

   from sparc.src.deepmd import evaluate_model_accuracy

   model = "iter_000000/01.train/training_1/frozen_model_1.pb"
   test  = "Dataset/validation_data"
   evaluate_model_accuracy(model, test)

.. automodule:: sparc.src.deepmd
   :members: evaluate_model_accuracy


References
----------

For more details on DeepMD-Kit, visit: https://github.com/deepmodeling/deepmd-kit

.. _qbc: https://docs.deepmodeling.com/projects/deepmd/en/stable/test/model-deviation.html
