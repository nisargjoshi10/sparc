from __future__ import annotations

import contextlib
import json
import os
import shutil
from pathlib import Path

import numpy as np
import pytest
from ase.io import read
from sparc.src.utils.read_incar import read_incar
from sparc.src.utils.utils import load_checkpoint

def test_read_incar(tmp_path: Path):
    
    repo_root = Path(__file__).resolve().parents[1]
    data_dir = repo_root / "tests" / "data" / "vasp_tmp"
    incar_file = "INCAR"
    incar = read_incar(data_dir/incar_file)

    assert type(incar.params) == dict, f"Invalid INCAR file"

def test_load_checkpoint(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[1]
    checkpoint_path = repo_root / "tests" / "data" / "water_checkpoint.pkl"
    atoms = read(repo_root / "tests" / "data" / "water.traj")

    updated_atoms, mdstep = load_checkpoint(atoms, checkpoint_path)

    assert isinstance(float(mdstep), float), f"Invalid step, check your file is correct."
