"""
Base Backend for AI Moderation
Abstract interface that all backends must implement
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseBackend(ABC):
    """Base class for all AI moderation backends"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize backend
        
        Args:
            api_key: Optional API key for external services
        """
        self.api_key = api_key
    
    @abstractmethod
    def check_toxicity(self, text: str, threshold: float = 0.7) -> Dict[str, Any]:
        """
        Check if text contains toxic content
        
        Args:
            text: Text to analyze
            threshold: Toxicity threshold (0.0-1.0)
        
        Returns:
            Dict with:
                - is_toxic (bool): Whether content is toxic
                - score (float): Toxicity score
                - backend (str): Backend name
                - error (str, optional): Error message if failed
                - details (dict, optional): Additional details
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return backend name"""
        pass
    
    @property
    def requires_api_key(self) -> bool:
        """Whether this backend requires an API key"""
        return False
