"""
Google Perspective API Backend
Uses Google's Perspective API for toxicity detection
"""

import requests
import logging
from typing import Dict, Any
from .base_backend import BaseBackend

logger = logging.getLogger(__name__)


class PerspectiveBackend(BaseBackend):
    """Toxicity detection using Google Perspective API"""
    
    API_URL = "https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze"
    
    @property
    def name(self) -> str:
        return 'perspective'
    
    @property
    def requires_api_key(self) -> bool:
        return True
    
    def check_toxicity(self, text: str, threshold: float = 0.7) -> Dict[str, Any]:
        """Check toxicity using Perspective API"""
        if not self.api_key:
            return {
                'is_toxic': False,
                'score': 0.0,
                'backend': self.name,
                'error': 'API key required'
            }
        
        if not text or not text.strip():
            return {
                'is_toxic': False,
                'score': 0.0,
                'backend': self.name
            }
        
        try:
            url = f"{self.API_URL}?key={self.api_key}"
            
            data = {
                'comment': {'text': text},
                'languages': ['en', 'he'],
                'requestedAttributes': {
                    'TOXICITY': {},
                    'SEVERE_TOXICITY': {},
                    'INSULT': {},
                    'PROFANITY': {},
                    'THREAT': {}
                }
            }
            
            response = requests.post(url, json=data, timeout=5)
            response.raise_for_status()
            
            result = response.json()
            
            # Get the highest score from all attributes
            scores = {}
            max_score = 0.0
            
            for attr_name, attr_data in result.get('attributeScores', {}).items():
                score = attr_data.get('summaryScore', {}).get('value', 0.0)
                scores[attr_name] = score
                max_score = max(max_score, score)
            
            is_toxic = max_score >= threshold
            
            if is_toxic:
                logger.info(f"🚫 Toxic content detected (Perspective): score={max_score:.2f}")
            
            return {
                'is_toxic': is_toxic,
                'score': max_score,
                'backend': self.name,
                'details': {
                    'attribute_scores': scores
                }
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Perspective API error: {e}")
            return {
                'is_toxic': False,
                'score': 0.0,
                'backend': self.name,
                'error': str(e)
            }
