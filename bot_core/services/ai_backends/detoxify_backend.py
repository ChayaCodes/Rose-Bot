"""
Detoxify Backend
Local ML model for toxicity detection (no API needed)
"""

raise ImportError("Detoxify backend removed; OpenAI is the only supported backend.")

import logging
from typing import Dict, Any
from .base_backend import BaseBackend

try:
    from detoxify import Detoxify
except ImportError:
    class Detoxify:  # type: ignore
        def __init__(self, *args, **kwargs):
            raise ImportError("Detoxify library not installed")

logger = logging.getLogger(__name__)


class DetoxifyBackend(BaseBackend):
    """Toxicity detection using Detoxify local ML model"""
    
    def __init__(self, api_key: str = None, model_type: str = 'multilingual'):
        """
        Initialize Detoxify backend
        
        Args:
            api_key: Not used, kept for interface compatibility
            model_type: Model type - 'original', 'unbiased', or 'multilingual' (recommended for Hebrew)
        """
        super().__init__(api_key)
        self.model_type = model_type
        self._model = None
    
    @property
    def name(self) -> str:
        return 'detoxify'
    
    @property
    def requires_api_key(self) -> bool:
        return False  # Local model, no API key needed
    
    def _load_model(self):
        """Lazy load the Detoxify model"""
        if self._model is None:
            try:
                self._model = Detoxify(self.model_type)
                logger.info(f"✅ Detoxify model '{self.model_type}' loaded")
            except ImportError:
                logger.error("❌ Detoxify not installed. Install with: pip install detoxify")
                raise ImportError("Detoxify library not installed")
        return self._model
    
    def check_toxicity(self, text: str, threshold: float = 0.7) -> Dict[str, Any]:
        """Check toxicity using Detoxify local model"""
        if not text or not text.strip():
            return {
                'is_toxic': False,
                'score': 0.0,
                'backend': self.name
            }
        
        try:
            model = self._load_model()
            
            # Get predictions
            results = model.predict(text)
            
            # Extract scores
            scores = {
                'toxicity': results.get('toxicity', 0.0),
                'severe_toxicity': results.get('severe_toxicity', 0.0),
                'obscene': results.get('obscene', 0.0),
                'threat': results.get('threat', 0.0),
                'insult': results.get('insult', 0.0),
                'identity_attack': results.get('identity_attack', 0.0)
            }
            
            # Get the highest toxicity score
            max_score = max(scores.values())
            
            is_toxic = max_score >= threshold
            
            if is_toxic:
                # Find which category triggered
                triggered = [k for k, v in scores.items() if v >= threshold]
                logger.info(f"🚫 Toxic content detected (Detoxify): score={max_score:.2f}, categories={triggered}")
            
            return {
                'is_toxic': is_toxic,
                'score': max_score,
                'backend': self.name,
                'details': {
                    'scores': scores,
                    'model_type': self.model_type
                }
            }
            
        except ImportError:
            logger.error("❌ Detoxify not installed")
            return {
                'is_toxic': False,
                'score': 0.0,
                'backend': self.name,
                'error': 'Detoxify library not installed. Install with: pip install detoxify'
            }
        except Exception as e:
            logger.error(f"❌ Detoxify error: {e}")
            return {
                'is_toxic': False,
                'score': 0.0,
                'backend': self.name,
                'error': str(e)
            }
