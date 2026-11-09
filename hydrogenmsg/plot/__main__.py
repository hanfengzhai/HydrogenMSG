"""Build manuscript panels.

Examples::

    python -m hydrogenmsg.plot              # all panels
    python -m hydrogenmsg.plot fig3a fig6b  # selected panels
    python -m hydrogenmsg.plot --list
"""

from __future__ import annotations

import argparse

from hydrogenmsg.plot.panels import DEFAULT_ORDER, PANELS, run_panels


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description="Build HydrogenMSG manuscript panels.")
    p.add_argument(
        "panels",
        nargs="*",
        help="Panel names (default: all). Example: fig3a fig11a",
    )
    p.add_argument("--list", action="store_true", help="List available panels and exit.")
    args = p.parse_args(argv)
    if args.list:
        for name in DEFAULT_ORDER:
            print(name)
        extra = sorted(set(PANELS) - set(DEFAULT_ORDER))
        for name in extra:
            print(name)
        return
    run_panels(args.panels or None)


if __name__ == "__main__":
    main()
