"""
OpenAI Moderation Backend
Uses OpenAI's Moderation API
"""

import requests
import logging
from typing import Dict, Any
from .base_backend import BaseBackend

logger = logging.getLogger(__name__)


class OpenAIBackend(BaseBackend):
    """Toxicity detection using OpenAI Moderation API"""
    
    API_URL = "https://api.openai.com/v1/moderations"
    
    @property
    def name(self) -> str:
        return 'openai'
    
    @property
    def requires_api_key(self) -> bool:
        return True
    
    def check_toxicity(self, text: str, threshold: float = 0.7) -> Dict[str, Any]:
        """Check toxicity using OpenAI Moderation API"""
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
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {'input': text}
            
            response = requests.post(self.API_URL, json=data, headers=headers, timeout=5)
            response.raise_for_status()
            
            result = response.json()
            
            if not result.get('results'):
                return {
                    'is_toxic': False,
                    'score': 0.0,
                    'backend': self.name,
                    'error': 'No results from API'
                }
            
            moderation = result['results'][0]
            
            # Check if any category is flagged
            is_flagged = moderation.get('flagged', False)
            
            # Get the highest category score
            category_scores = moderation.get('category_scores', {})
            max_score = max(category_scores.values()) if category_scores else 0.0
            
            # Get flagged categories
            categories = moderation.get('categories', {})
            flagged_categories = [cat for cat, flagged in categories.items() if flagged]
            
            is_toxic = is_flagged or (max_score >= threshold)
            
            if is_toxic:
                logger.info(f"🚫 Toxic content detected (OpenAI): flagged={is_flagged}, score={max_score:.4f}")
            
            return {
                'is_toxic': is_toxic,
                'score': max_score,
                'backend': self.name,
                'details': {
                    'flagged': is_flagged,
                    'flagged_categories': flagged_categories,
                    'category_scores': category_scores
                }
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ OpenAI API error: {e}")
            return {
                'is_toxic': False,
                'score': 0.0,
                'backend': self.name,
                'error': str(e)
            }
