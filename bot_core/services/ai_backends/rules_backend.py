"""Deprecated rules backend (disabled)."""

from typing import Dict, Any
from .base_backend import BaseBackend


class RulesBackend(BaseBackend):
    """Rules backend is deprecated and should not be used."""

    @property
    def name(self) -> str:
        return 'rules'

    def check_toxicity(self, text: str, threshold: float = 0.7) -> Dict[str, Any]:
        return {
            'is_toxic': False,
            'score': 0.0,
            'backend': self.name,
            'details': {'deprecated': True}
        }
