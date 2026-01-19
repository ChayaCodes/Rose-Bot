"""
Rules-based Backend
Simple regex-based toxicity detection
"""

import re
import logging
from typing import Dict, Any
from .base_backend import BaseBackend

logger = logging.getLogger(__name__)


class RulesBackend(BaseBackend):
    """Rule-based toxicity detection using regex patterns"""
    
    # Toxic patterns for different languages
    TOXIC_PATTERNS = [
        # Hebrew toxic patterns
        r'\b(דפוק|מניאק|זין|כוס|חרא|לעזאזל|בן זונה|שרמוטה|מזדיין|לך תזדיין|קקי|חתיכת|טמבל)\b',
        # English toxic patterns
        r'\b(fuck|shit|damn|bitch|asshole|idiot|stupid|retard|cunt|whore|slut|bastard|piss)\b',
        # Spam patterns
        r'(http|https|www\.)\S+',
        r'(\d{10,})',  # Long numbers (phone/spam)
        # Repeated characters (spam)
        r'(.)\1{5,}',
    ]
    
    @property
    def name(self) -> str:
        return 'rules'
    
    def check_toxicity(self, text: str, threshold: float = 0.7) -> Dict[str, Any]:
        """Check toxicity using regex patterns"""
        if not text or not text.strip():
            return {
                'is_toxic': False,
                'score': 0.0,
                'backend': self.name
            }
        
        text_lower = text.lower()
        matched_patterns = []
        
        for pattern in self.TOXIC_PATTERNS:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                matched_patterns.append({
                    'pattern': pattern,
                    'matches': matches
                })
        
        if matched_patterns:
            # Calculate score based on number of matches
            score = min(0.9, 0.5 + (len(matched_patterns) * 0.2))
            
            logger.info(f"🚫 Toxic content detected (rules): {len(matched_patterns)} patterns matched")
            
            return {
                'is_toxic': True,
                'score': score,
                'backend': self.name,
                'details': {
                    'matched_patterns': len(matched_patterns),
                    'patterns': matched_patterns
                }
            }
        
        return {
            'is_toxic': False,
            'score': 0.0,
            'backend': self.name
        }
