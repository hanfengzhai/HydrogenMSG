"""Build manuscript panels.

Examples::

    python -m hydrogenmsg.plot                 # all companion panels
    python -m hydrogenmsg.plot --manuscript    # panels cited in the TeX
    python -m hydrogenmsg.plot fig3a fig6b
    python -m hydrogenmsg.plot --list
    python -m hydrogenmsg.plot --meshes
"""

from __future__ import annotations

import argparse

from hydrogenmsg.plot.panels import (
    DEFAULT_ORDER,
    MANUSCRIPT_ORDER,
    PANELS,
    run_panels,
)


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description="Build HydrogenMSG manuscript panels.")
    p.add_argument(
        "panels",
        nargs="*",
        help="Panel names (default: all companion panels).",
    )
    p.add_argument(
        "--manuscript",
        action="store_true",
        help="Build only panels included by the current manuscript TeX.",
    )
    p.add_argument("--meshes", action="store_true", help="Also write FEM mesh figures.")
    p.add_argument("--list", action="store_true", help="List available panels and exit.")
    args = p.parse_args(argv)

    if args.list:
        print("# manuscript")
        for name in MANUSCRIPT_ORDER:
            print(name)
        print("# other companion panels")
        for name in DEFAULT_ORDER:
            if name not in MANUSCRIPT_ORDER:
                print(name)
        return

    if args.panels:
        names = list(args.panels)
    elif args.manuscript:
        names = list(MANUSCRIPT_ORDER)
    else:
        names = None
    run_panels(names)

    if args.meshes:
        from hydrogenmsg.plot import meshes

        print("=== FEM meshes ===")
        meshes.main()


if __name__ == "__main__":
    main()
