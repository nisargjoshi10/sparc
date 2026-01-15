from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
import warnings
from ase.config import ASEEnvDeprecationWarning
import pytest

from sparc.src.calculator import dft_calculator
############################################################

def _which(name: str) -> str | None:
    return shutil.which(name)

############################################################
#                       CP2K                               #
############################################################
def test_cp2k_calculator_wrapper(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """
        Runs CP2K via SPARC dft_calculator module using a template file.
        Skips if cp2k_shell.psmp is not available.
    """
    cp2k_exe = _which("cp2k_shell.psmp")
    if cp2k_exe is None:
        pytest.skip("cp2k_shell.psmp not found in PATH")

    # locate data directory
    repo_root = Path(__file__).resolve().parents[1]
    data_dir = repo_root / "tests" / "data" / "cp2k_tmp"

    cp2k_inp = data_dir / "cp2k_template.inp"
    basis = data_dir / "BASIS_SET"
    pot = data_dir / "GTH_POTENTIALS"
    results = data_dir / "results.json"

    for f in (cp2k_inp, basis, pot, results):
        assert f.exists(), f"Missing: {f}"

    reference = json.loads(results.read_text())

    # run in a temp directory
    run_dir = tmp_path / "run"
    run_dir.mkdir(exist_ok=True)

    shutil.copy(cp2k_inp, run_dir / "cp2k_template.inp")
    shutil.copy(basis, run_dir / "BASIS_SET")
    shutil.copy(pot, run_dir / "GTH_POTENTIALS")

    monkeypatch.chdir(run_dir)

    # Build a H2O molecule for test run
    from ase.build import molecule

    atoms = molecule("H2O")
    atoms.center(vacuum=3.0)

    # configure calculator
    config = {
        "dft_calculator": {
            "name": "CP2K",
            "exe_command": cp2k_exe,
        },
        "cp2k": {
            "label": str(run_dir / "cp2k" / "job"),
        },
    }

    calc = dft_calculator(config, print_screen=False)
    assert calc is not None, "returned None for CP2K calculator setup"

    atoms.calc = calc

    # Compute Energy/Forces
    energy_ev = atoms.get_potential_energy()
    forces = atoms.get_forces()
    max_force = float((forces**2).sum(axis=1).max() ** 0.5)

    # sanity check
    assert (run_dir / "cp2k").exists(), "CP2K output directory was not created"

    # compare against reference output
    ref_energy = float(reference["energy_ev"])
    ref_force = float(reference["max_force_evA"])

    energy_tol = float(reference.get("energy_tol_ev", 1e-3))
    force_tol = float(reference.get("max_force_tol_evA", 0.05))

    dE = energy_ev - ref_energy
    dF = max_force - ref_force

    print("\nCP2K regression check:")
    print("  Energy (eV):")
    print(f"    reference = {ref_energy:.12f}")
    print(f"    current   = {energy_ev:.12f}")
    print(f"    diff      = {dE:.6e} eV (tol = {energy_tol:.3e})")

    print("  Max force (eV/Ang.):")
    print(f"    reference = {ref_force:.12f}")
    print(f"    current   = {max_force:.12f}")
    print(rf"    diff      = {dF:.6e} eV/Ang. (tol = {force_tol:.3e})")

    assert abs(dE) <= energy_tol, (
        "Energy mismatch:\n"
        f"  reference = {ref_energy:.12f} eV\n"
        f"  current   = {energy_ev:.12f} eV\n"
        f"  diff E = {dE:.6e} eV (tol = {energy_tol:.3e})"
    )

    assert abs(dF) <= force_tol, (
        "Max force mismatch:\n"
        f"  reference = {ref_force:.12f} eV/Ang.\n"
        f"  current   = {max_force:.12f} eV/Ang.\n"
        f"  diff F = {dF:.6e} eV/Ang. (tol = {force_tol:.3e})"
    )
############################################################
#                       VASP                               #
############################################################
def test_vasp_calculator_wrapper(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """
        Runs VASP via SPARC dft_calculator module using a INCAR template.
        Skips if vasp_std is not available.
    """
    vasp_exe = _which("vasp_std")
    if vasp_exe is None:
        pytest.skip("vasp_std not found in PATH")

    # locate data directory
    repo_root = Path(__file__).resolve().parents[1]
    data_dir = repo_root / "tests" / "data" / "vasp_tmp"

    incar = data_dir / "INCAR"
    results = data_dir / "results.json"

    for f in (incar, results):
        assert f.exists(), f"Missing: {f}"

    reference = json.loads(results.read_text())

    # run in a temp directory
    run_dir = tmp_path / "run"
    run_dir.mkdir(exist_ok=True)

    shutil.copy(incar, run_dir / "INCAR")

    # (We do not enforce POTCAR in the repo since it is licensed.)
    # Please read the ASE documentation for [VASP](https://ase-lib.org/gettingstarted/external_calculators/ext_intro.html)
    vasp_pp_path = os.getenv("VASP_PP_PATH")
    if not vasp_pp_path:
            pytest.skip("Missing POTCAR file VASP_PP_PATH not set")
    monkeypatch.setenv("VASP_PP_PATH", vasp_pp_path)
        
    monkeypatch.chdir(run_dir)

    # Build a H2O molecule for test run
    from ase.build import molecule

    atoms = molecule("H2O")
    atoms.center(vacuum=3.0)
    atoms.set_pbc([True, True, True])

    # configure calculator
    config = {
        "dft_calculator": {
            "name": "VASP",
            "prec": "Normal",
            "kgamma": True,
            "incar_file": "INCAR",
            "exe_command": vasp_exe,
        }
    }

    calc = dft_calculator(config, print_screen=False)
    assert calc is not None, "returned None for VASP calculator setup"

    atoms.calc = calc
    warnings.filterwarnings(
    "ignore",
    category=ASEEnvDeprecationWarning,
    )
    # Compute Energy/Forces
    energy_ev = atoms.get_potential_energy()
    forces = atoms.get_forces()
    max_force = float((forces**2).sum(axis=1).max() ** 0.5)

    # sanity check
    assert (run_dir / "vasp").exists() or (run_dir / "OUTCAR").exists(), "VASP output was not created"

    # compare against reference output
    ref_energy = float(reference["energy_ev"])
    ref_force = float(reference["max_force_evA"])

    energy_tol = float(reference.get("energy_tol_ev", 1e-3))
    force_tol = float(reference.get("max_force_tol_evA", 0.05))

    dE = energy_ev - ref_energy
    dF = max_force - ref_force

    print("\nVASP regression check:")
    print("  Energy (eV):")
    print(f"    reference = {ref_energy:.12f}")
    print(f"    current   = {energy_ev:.12f}")
    print(f"    diff      = {dE:.6e} eV (tol = {energy_tol:.3e})")

    print("  Max force (eV/Ang.):")
    print(f"    reference = {ref_force:.12f}")
    print(f"    current   = {max_force:.12f}")
    print(rf"    diff      = {dF:.6e} eV/Ang. (tol = {force_tol:.3e})")

    assert abs(dE) <= energy_tol, (
        "Energy mismatch:\n"
        f"  reference = {ref_energy:.12f} eV\n"
        f"  current   = {energy_ev:.12f} eV\n"
        f"  diff E = {dE:.6e} eV (tol = {energy_tol:.3e})"
    )

    assert abs(dF) <= force_tol, (
        "Max force mismatch:\n"
        f"  reference = {ref_force:.12f} eV/Ang.\n"
        f"  current   = {max_force:.12f} eV/Ang.\n"
        f"  diff F = {dF:.6e} eV/Ang. (tol = {force_tol:.3e})"
    )
