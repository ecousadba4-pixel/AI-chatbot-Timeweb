"""Гарантирует доступ к локальным заглушкам внешних зависимостей."""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(__file__)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
