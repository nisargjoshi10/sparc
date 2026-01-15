from __future__ import annotations

import contextlib
import json
import os
import shutil
from pathlib import Path

import numpy as np
import pytest
from ase.io import read


def _which(name: str) -> str | None:
    return shutil.which(name)


def test_deepmd_pipeline(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """
    End-to-end test:
      ASE trajectory -> get_data -> DeepMD npy dataset
      DeepMD input.json -> deepmd_training -> frozen/compressed models

    Skips if DeepMD CLI is not available (dp).
    """
    dp_cli = _which("dp")
    if dp_cli is None:
        pytest.skip("'dp' (DeePMD-kit CLI) not found in PATH")

    # locate data folder
    repo_root = Path(__file__).resolve().parents[1]
    data_dir = repo_root / "tests" / "data" / "mlp"

    traj_file = data_dir / "AseMD.traj"
    input_json = data_dir / "input.json"

    assert traj_file.exists(), f"Missing: {traj_file}"
    assert input_json.exists(), f"Missing: {input_json}"

    # run inside a temp folder
    run_dir = tmp_path / "run"
    run_dir.mkdir()

    run_traj = run_dir / "AseMD.traj"
    run_input = run_dir / "input.json"
    shutil.copy(traj_file, run_traj)
    shutil.copy(input_json, run_input)

    monkeypatch.chdir(run_dir)

    # split dataset
    np.random.seed(12345)

    # infer atom types from first frame of trajectory
    atoms0 = read(str(run_traj), index=0)
    atoms = set()
    atom_types = []
    for s in atoms0.get_chemical_symbols():
        if s not in atoms:
            atom_types.append(s)
            atoms.add(s)

    dataset_dir = run_dir / "Dataset"
    training_dir = str(run_dir / "Training")

    # silence all stdout/stderr during run
    with open(os.devnull, "w") as devnull, contextlib.redirect_stdout(
        devnull
    ), contextlib.redirect_stderr(devnull):
        # ===================
        # 1) data processing
        # ===================
        from sparc.src.data_processing import get_data

        get_data(
            ase_traj=str(run_traj),
            dir_name=str(dataset_dir),
            skip_min=0,
            skip_max=None,
        )

        # ===================
        # 2) DeepMD training
        # ===================
        from sparc.src.deepmd import deepmd_training

        frozen_model_name = deepmd_training(
            active_learning=False,
            datadir=str(dataset_dir),
            atom_types=atom_types,
            training_dir=training_dir,
            num_models=2,
            input_file=str(run_input),
        )

    # ===================
    # 3) Assert dataset
    # ===================
    training_data = dataset_dir / "training_data"
    validation_data = dataset_dir / "validation_data"

    assert training_data.exists(), f"Missing: {training_data}"
    assert validation_data.exists(), f"Missing: {validation_data}"
    assert any(training_data.rglob("*.npy")), "No .npy files in training_data"
    assert any(validation_data.rglob("*.npy")), "No .npy files in validation_data"

    # ===================
    # 4) Assert training
    # ===================
    train_root = Path(training_dir)
    assert train_root.exists(), f"Missing training_dir: {train_root}"

    # model training in Training/training_1, Training/training_2 ...
    for i in (1, 2):
        model_dir = train_root / f"training_{i}"
        assert model_dir.exists(), f"Missing: {model_dir}"

        frozen = model_dir / f"frozen_model_{i}.pb"
        compressed = model_dir / f"frozen_model_compressed_{i}.pb"

        assert frozen.exists(), f"Missing frozen model: {frozen}"
        assert compressed.exists(), f"Missing compressed model: {compressed}"

    # deepmd_training returns frozen_model_name
    assert isinstance(frozen_model_name, str) and frozen_model_name.endswith(".pb")
