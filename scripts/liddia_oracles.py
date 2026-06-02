"""Simple oracle calls using evaluator tools, with RDKit fallbacks."""

from rdkit import Chem
import math
import pickle
from pathlib import Path

from rdkit.Chem import Crippen, Descriptors, Lipinski, QED, rdMolDescriptors

try:
    from evaluator.tools.physchem import calculate_sascore
except ImportError:
    _fscores = None

    def _fragment_scores():
        global _fscores
        if _fscores is None:
            scores_path = Path(__file__).resolve().parent / "oracle" / "fpscores.pkl"
            raw_scores = pickle.load(open(scores_path, "rb"))
            _fscores = {}
            for row in raw_scores:
                for bit_id in row[1:]:
                    _fscores[bit_id] = float(row[0])
        return _fscores

    def calculate_sascore(smi):
        mol = Chem.MolFromSmiles(smi)
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
        sascore = score1 + score2 + score3

        min_score = -4.0
        max_score = 2.5
        sascore = 11.0 - (sascore - min_score + 1) / (max_score - min_score) * 9.0
        if sascore > 8.0:
            sascore = 8.0 + math.log(sascore + 1.0 - 9.0)
        if sascore > 10.0:
            sascore = 10.0
        if sascore < 1.0:
            sascore = 1.0
        return sascore


def _mol(smi):
    return Chem.MolFromSmiles(smi)


def _toxicity(smi):
    try:
        from evaluator.tools.admet import predict_toxicity
    except ImportError as exc:
        raise ImportError(
            "ADMET oracles require evaluator.tools.admet to be importable."
        ) from exc
    return predict_toxicity(smi)

def qed(smi):
    mol = _mol(smi)
    if mol is None:
        return 0
    return QED.qed(mol) or 0


def sascore(smi):
    sa = calculate_sascore(smi) or 10
    return max(0, 10 - sa)


def mol_wt(smi):
    mol = _mol(smi)
    if mol is None:
        return 0
    return Descriptors.MolWt(mol) or 0


def logp(smi):
    mol = _mol(smi)
    if mol is None:
        return 0
    val = Crippen.MolLogP(mol)
    return max(val, 0)

def tpsa(smi):
    mol = _mol(smi)
    if mol is None:
        return 0
    return Descriptors.TPSA(mol) or 0


def hbd(smi):
    mol = _mol(smi)
    if mol is None:
        return 0
    return Lipinski.NumHDonors(mol) or 0


def hba(smi):
    mol = _mol(smi)
    if mol is None:
        return 0
    return Lipinski.NumHAcceptors(mol) or 0


def rot_bonds(smi):
    mol = _mol(smi)
    if mol is None:
        return 0
    return Lipinski.NumRotatableBonds(mol) or 0


def herg(smi):
    tox = _toxicity(smi)
    return 1 - (tox.get("hERG") or 0)


def dili(smi):
    tox = _toxicity(smi)
    return 1 - (tox.get("DILI") or 0)


def clintox(smi):
    tox = _toxicity(smi)
    return 1 - (tox.get("ClinTox") or 0)


def mutagenicity(smi):
    tox = _toxicity(smi)
    return 1 - (tox.get("Mutagenicity") or 0)


def carcinogens(smi):
    tox = _toxicity(smi)
    return 1 - (tox.get("Carcinogens") or 0)
