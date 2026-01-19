"""
Azure Content Safety Backend
Uses Azure Cognitive Services Content Safety API
"""

import requests
import logging
from typing import Dict, Any
from .base_backend import BaseBackend

logger = logging.getLogger(__name__)


class AzureBackend(BaseBackend):
    """Toxicity detection using Azure Content Safety"""
    
    def __init__(self, api_key: str = None, endpoint: str = None):
        """
        Initialize Azure backend
        
        Args:
            api_key: Azure subscription key
            endpoint: Azure endpoint URL (e.g., https://your-resource.cognitiveservices.azure.com/)
        """
        super().__init__(api_key)
        self.endpoint = endpoint or "https://your-resource.cognitiveservices.azure.com/"
    
    @property
    def name(self) -> str:
        return 'azure'
    
    @property
    def requires_api_key(self) -> bool:
        return True
    
    def check_toxicity(self, text: str, threshold: float = 0.7) -> Dict[str, Any]:
        """Check toxicity using Azure Content Safety"""
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
            url = f"{self.endpoint.rstrip('/')}/contentsafety/text:analyze?api-version=2023-10-01"
            
            headers = {
                'Ocp-Apim-Subscription-Key': self.api_key,
                'Content-Type': 'application/json'
            }
            
            data = {
                'text': text,
                'categories': ['Hate', 'SelfHarm', 'Sexual', 'Violence']
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=5)
            response.raise_for_status()
            
            result = response.json()
            
            # Azure returns severity levels (0-6), convert to 0-1 scale
            categories = {}
            max_severity = 0
            
            for category in result.get('categoriesAnalysis', []):
                cat_name = category.get('category')
                severity = category.get('severity', 0)
                categories[cat_name] = severity
                max_severity = max(max_severity, severity)
            
            score = max_severity / 6.0  # Normalize to 0-1
            is_toxic = score >= threshold
            
            if is_toxic:
                logger.info(f"🚫 Toxic content detected (Azure): score={score:.2f}")
            
            return {
                'is_toxic': is_toxic,
                'score': score,
                'backend': self.name,
                'details': {
                    'categories': categories,
                    'max_severity': max_severity
                }
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Azure API error: {e}")
            return {
                'is_toxic': False,
                'score': 0.0,
                'backend': self.name,
                'error': str(e)
            }
