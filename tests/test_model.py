from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import numpy as np

from ase.io import read
from sparc.src.deepmd import setup_DeepPotential
from sparc.src.ase_md import NoseNVT, LangevinNVT
###############################################################

def test_mlmd_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):

    root_dir = Path(__file__).resolve().parents[1]

    data_dir    = root_dir / "tests" / "data" / "mlp"
    model_dir   = root_dir / "tests" / "data" / "mlmd"
    traj_file   = "AseMD.traj"
    model_name  = "frozen_model_1.pb"
    model       = model_dir / model_name

    # run inside a temp folder
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    
    atoms = read(data_dir/traj_file, index=0)
    system, calc = setup_DeepPotential(atoms=atoms,
                                       model_path = model_dir,
                                       model_name = model_name)
    
    assert calc is not None, "returned None from Deepmd calculator setup"

    # compute energy/forces
    energy = atoms.get_potential_energy()
    forces = atoms.get_forces()
    
    ref_energy  = -36.094413
    ref_force = np.array([[-0.000000e+00, -2.246000e-03, -6.007548e+00],
                            [-0.000000e+00,  1.930980e-01,  1.280370e-01],
                            [ 1.691720e-01, -9.957000e-02,  1.228540e-01],
                            [-1.691720e-01, -9.957000e-02,  1.228540e-01],
                            [-1.840700e-02,  7.246000e-03, -1.002100e-02],
                            [-0.000000e+00, -1.636200e-02, -1.161900e-02],
                            [ 1.840700e-02,  7.246000e-03, -1.002100e-02],
                            [-0.000000e+00,  1.015800e-02,  5.665467e+00]])
    
    dE = ref_energy - energy
    
    print("\nDeepPotential regression check:")
    print(f"   Energy (eV): {energy:.6f}")
    print(f"   Forces (eV/Ang.): \n {forces}")
    
    # sanity check
    assert energy is not None and np.isfinite(energy), "energy is not computed check model"
    assert forces is not None and np.all(np.isfinite(forces)), "forces are not computed"
    
    assert abs(dE) <= 1e-4, (
        "Energy mismatch:\n"
        f"  reference = {ref_energy:.12f} eV\n"
        f"  current   = {energy:.12f} eV\n"
        f"  diff E = {dE:.6e} eV (tol = {1.e-4:.3e})"
    )
    assert np.allclose(np.array(forces), ref_force, atol=1e-3)
            
    # check ML/MD modules
    dyn_nvt = NoseNVT(atoms=system, temperature=330)
    results = dyn_nvt.run(1)
    print(results)
    assert results is not None, "Error in ML/MD module"
    
    dyn_lag = LangevinNVT(atoms=system, temperature=330, friction=0.01)
    results = dyn_lag.run(1)
    print(results)
    assert results is not None, "Error in ML/MD module"
    
    

