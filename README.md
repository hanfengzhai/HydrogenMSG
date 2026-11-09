# HydrogenMSG

Companion **code** for the IJSS manuscript on hydrogen transport and trapping
in mechanism-based strain gradient (MSG) plasticity. The manuscript is published
separately; this repository contains only the theory, FEM solvers, and figure
generators.

## Layout

```
hydrogenmsg/
  analytics.py      # closed-form MSG–Oriani model
  fem/              # CMSG finite-element solvers
    canonical.py    # torsion / bending Q9 checks
    void.py         # spherical void
    slit.py         # Mode-I slit + HELP
  plot/             # manuscript figure library
    panels.py       # panel registry
    analytical.py / schematics.py / fem_panels.py / …
output/             # generated PDF/PNG (gitignored)
make_figures.py     # thin CLI wrapper
```

## Install

```bash
python3 -m pip install -e .
```

Or just install the dependencies:

```bash
python3 -m pip install -r requirements.txt
```

## Reproduce the figures

```bash
python3 make_figures.py                 # all panels → output/
python3 -m hydrogenmsg.plot fig3a       # one panel
python3 -m hydrogenmsg.plot --list
```

## FEM verification

```bash
python3 -m hydrogenmsg.fem.void
python3 -m hydrogenmsg.fem.canonical
python3 -m hydrogenmsg.fem.slit
```
