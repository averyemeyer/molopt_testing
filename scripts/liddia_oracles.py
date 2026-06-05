"""MolOpt scalar objectives backed by LIDDIA evaluator tool functions.

The evaluator tools are the source of truth for raw physicochemical and ADMET
values. These wrappers only adapt direction where MolOpt needs a single scalar
objective where higher is better.
"""

import hashlib
import math
import pickle
import sys
from pathlib import Path


def _ensure_evaluator_on_path():
    """Find the workspace parent that contains evaluator/ when run from mol-opt."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "evaluator").is_dir():
            path = str(parent)
            if path not in sys.path:
                sys.path.insert(0, path)
            return


_ensure_evaluator_on_path()

from evaluator.tools import (  # noqa: E402
    calculate_hba,
    calculate_hbd,
    calculate_logp,
    calculate_molecular_weight,
    calculate_qed,
    calculate_rot_bonds,
    calculate_sascore,
    calculate_tpsa,
    predict_toxicity,
)

_fscores = None


def _fragment_scores():
    global _fscores
    if _fscores is None:
        scores_path = Path(__file__).resolve().parent / "oracle" / "fpscores.pkl"
        with scores_path.open("rb") as handle:
            raw_scores = pickle.load(handle)
        _fscores = {}
        for row in raw_scores:
            for bit_id in row[1:]:
                _fscores[bit_id] = float(row[0])
    return _fscores


def _fallback_sascore(smiles):
    from rdkit import Chem
    from rdkit.Chem import rdMolDescriptors

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None

    fscores = _fragment_scores()
    fp = rdMolDescriptors.GetMorganFingerprint(mol, 2)
    fps = fp.GetNonzeroElements()
    score1 = sum(fscores.get(bit_id, -4) * value for bit_id, value in fps.items())
    score1 /= max(sum(fps.values()), 1)

    n_atoms = mol.GetNumAtoms()
    n_chiral = len(Chem.FindMolChiralCenters(mol, includeUnassigned=True))
    ring_info = mol.GetRingInfo()
    n_bridgeheads = rdMolDescriptors.CalcNumBridgeheadAtoms(mol)
    n_spiro = rdMolDescriptors.CalcNumSpiroAtoms(mol)
    n_macrocycles = sum(1 for ring in ring_info.AtomRings() if len(ring) > 8)

    score2 = 0.0
    score2 -= n_atoms**1.005 - n_atoms
    score2 -= math.log10(n_chiral + 1)
    score2 -= math.log10(n_spiro + 1)
    score2 -= math.log10(n_bridgeheads + 1)
    score2 -= math.log10(2) if n_macrocycles > 0 else 0

    n_fragments = len(fps)
    score3 = math.log(float(n_atoms) / n_fragments) * 0.5 if n_atoms > n_fragments else 0
    sa_score = score1 + score2 + score3

    min_score = -4.0
    max_score = 2.5
    sa_score = 11.0 - (sa_score - min_score + 1) / (max_score - min_score) * 9.0
    if sa_score > 8.0:
        sa_score = 8.0 + math.log(sa_score + 1.0 - 9.0)
    if sa_score > 10.0:
        sa_score = 10.0
    if sa_score < 1.0:
        sa_score = 1.0
    return sa_score


def _raw_sascore(smiles):
    raw_sa = calculate_sascore(smiles)
    if raw_sa is not None:
        return raw_sa
    return _fallback_sascore(smiles)


def _as_score(value, default=0.0):
    if value is None:
        return default
    return float(value)


def _toxicity(smiles):
    return predict_toxicity(smiles)


def _toxicity_safety(smiles, endpoint):
    """Convert toxicity probability to safety; missing predictions are unsafe."""
    tox = _toxicity(smiles)
    return 1.0 - _as_score(tox.get(endpoint), default=1.0)


def qed(smiles):
    """Raw QED from evaluator; higher is better."""
    return _as_score(calculate_qed(smiles))


def sascore(smiles):
    """Synthetic-accessibility desirability: raw SA is inverted."""
    raw_sa = _raw_sascore(smiles)
    if raw_sa is None:
        return 0.0
    return max(0.0, 10.0 - float(raw_sa))


def mol_wt(smiles):
    """Raw exact molecular weight from evaluator."""
    return _as_score(calculate_molecular_weight(smiles))


def logp(smiles):
    """Raw LogP from evaluator, clipped at zero for maximize-style benchmarking."""
    return max(_as_score(calculate_logp(smiles)), 0.0)


def tpsa(smiles):
    """Raw TPSA from evaluator."""
    return _as_score(calculate_tpsa(smiles))


def hbd(smiles):
    """Raw hydrogen-bond donor count from evaluator."""
    return _as_score(calculate_hbd(smiles))


def hba(smiles):
    """Raw hydrogen-bond acceptor count from evaluator."""
    return _as_score(calculate_hba(smiles))


def rot_bonds(smiles):
    """Raw rotatable-bond count from evaluator."""
    return _as_score(calculate_rot_bonds(smiles))


def generation_probe(smiles):
    """Near-zero-cost deterministic score for optimizer overhead timing."""
    digest = hashlib.blake2b(smiles.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, byteorder="big") / float((1 << 64) - 1)


def herg(smiles):
    """hERG safety desirability: 1 - evaluator toxicity probability."""
    return _toxicity_safety(smiles, "hERG")


def dili(smiles):
    """DILI safety desirability: 1 - evaluator toxicity probability."""
    return _toxicity_safety(smiles, "DILI")


def clintox(smiles):
    """ClinTox safety desirability: 1 - evaluator toxicity probability."""
    return _toxicity_safety(smiles, "ClinTox")


def mutagenicity(smiles):
    """Mutagenicity safety desirability: 1 - evaluator toxicity probability."""
    return _toxicity_safety(smiles, "Mutagenicity")


def carcinogens(smiles):
    """Carcinogenicity safety desirability: 1 - evaluator toxicity probability."""
    return _toxicity_safety(smiles, "Carcinogens")
