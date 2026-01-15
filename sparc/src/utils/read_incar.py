# read_incar.py
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_TRUE = {".true.", "true", "t"}
_FALSE = {".false.", "false", "f"}

@dataclass(frozen=True)
class Incar:
    """
        Map INCAR keywords in a dictonary.
    """
    params: dict[str, Any]


def _strip_comment(s: str) -> str:
    """
        Remove comments from VASP/INCAR file (startswith # or !)
    """
    for marker in ("!", "#"):
        if marker in s:
            s = s.split(marker, 1)[0]
    return s.strip()


def _parse_scalar(token: str) -> Any:
    """
        Parse a single token (INCAR keyword) which can be:
        - Bollean
        - String
        - Integer
        - Float
        If keyword not found, fallback to raw token.
    """
    t = token.strip()
    low = t.lower()

    if low in _TRUE:
        return True
    if low in _FALSE:
        return False

    if (t.startswith('"') and t.endswith('"')) or (t.startswith("'") and t.endswith("'")):
        return t[1:-1]

    try:
        if any(c in t for c in (".", "e", "E")):
            return float(t)
        return int(t)
    except ValueError:
        return t


def _expand_multiplier(tok: str) -> list[Any]:
    """
        Parse VASP style shorthand expression
        Example: MAGMOM = 4>0 4*1 is same as MAGMOM 0 0 0 1 1 1 1
    """
    if "*" in tok:
        left, right = tok.split("*", 1)
        if left.strip().isdigit():
            return [_parse_scalar(right)] * int(left)
    return [_parse_scalar(tok)]


def _parse_value(raw: str) -> Any:
    """
        Parse single/mutiple tokens separated by whitespace
    """
    tokens = raw.strip().split()
    if not tokens:
        return ""

    values: list[Any] = []
    for tok in tokens:
        values.extend(_expand_multiplier(tok))

    return values[0] if len(values) == 1 else values


def read_incar(path: str | Path) -> Incar:
    """
        Read and parse INCAR file.
    """
    path = Path(path)
    params: dict[str, Any] = {}

    for line in path.read_text().splitlines():
        line = _strip_comment(line)
        if not line:
            continue
        # allow comma separation (eg. ENCUT=300; ISMEAR=0; SIGMA=0.05)
        for chunk in (c.strip() for c in line.split(";")):
            if not chunk:
                continue

            if "=" in chunk:
                key, val = chunk.split("=", 1)
            else:
                parts = chunk.split(None, 1)
                key, val = parts[0], parts[1] if len(parts) > 1 else ""

            params[key.strip().upper()] = _parse_value(val)

    return Incar(params=params)


# Public API
def parse_incar(path: str | Path) -> dict[str, Any]:
    """
    Parse an INCAR file and return a plain dictonary with keys.

    Parameters
    ----------
    path: str or pathlib.Path
        Path to the INCAR file.

    Return
    ------
    dict[str, Any]
        Dictionary of INCAR parameters.
    """
    incar = read_incar(path)
    return {k.lower(): v for k, v in incar.params.items()}

# Example usage
if __name__ == "__main__":
    try:
        # Parse INCAR and print parameters
        incar_params = parse_incar("INCAR")

    except Exception as e:
        print(f"Error reading INCAR file: {e!s}")

    print(incar_params)


