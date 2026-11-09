"""Put scripts/ and scripts/figures/ on sys.path for ad hoc runners."""

from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_SCRIPTS = os.path.dirname(_HERE)
for p in (_HERE, _SCRIPTS):
    if p not in sys.path:
        sys.path.insert(0, p)
