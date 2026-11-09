# HydrogenMSG

Companion **code** for the IJSS manuscript on hydrogen transport and trapping
in mechanism-based strain gradient (MSG) plasticity. The manuscript itself is
published separately by the journal; this repository does not contain the paper.

## What is included

| Path | Role |
|------|------|
| `scripts/msg_hydrogen.py` | Analytical MSG–Oriani model (torsion, bending, void, cavitation) |
| `scripts/fem_canonical.py` | Q9 checks for torsion / bending FEM panels |
| `scripts/fem_msg.py` | Axisymmetric void FEM |
| `scripts/fem_slit.py` | Plane-strain Mode-I slit FEM (HELP) |
| `scripts/figures/` | One script per manuscript subfigure |
| `figures/` | Generated PDF/PNG panels (gitignored; create by running the scripts) |

## Reproduce the figures

```bash
python3 -m pip install -r requirements.txt
python3 scripts/make_figures.py
```

Single panel:

```bash
python3 scripts/figures/fig3a.py
```

## FEM verification

```bash
python3 scripts/fem_msg.py
python3 scripts/fem_canonical.py
```
