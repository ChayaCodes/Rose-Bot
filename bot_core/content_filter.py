"""
AI-powered Content Moderation
Detects toxic, spam, sexual, threatening content

Backend:
- OpenAI Moderation API
"""

import re
import logging
import os
from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Types of problematic content"""
    TOXIC = "toxic"
    SEVERE_TOXIC = "severe_toxic"
    OBSCENE = "obscene"
    THREAT = "threat"
    INSULT = "insult"
    IDENTITY_HATE = "identity_hate"
    SEXUAL = "sexual"
    SPAM = "spam"
    PROMOTION = "promotion"


@dataclass
class ModerationResult:
    """Result of content moderation check"""
    is_flagged: bool
    violation_type: Optional[ContentType]
    confidence: float
    reason: str
    scores: Dict[str, float]


class ContentModerator:
    """
    AI-powered content moderation
    Supports a single backend:
    - openai: OpenAI Moderation API
    """
    
    def __init__(self, backend: str = 'openai', api_key: Optional[str] = None):
        """
        Initialize content moderator
        
        Args:
            backend: Moderation backend ('openai')
            api_key: OpenAI API key
        """
        self.backend = backend
        self.api_key = api_key or os.getenv(f'{backend.upper()}_API_KEY')
        self.ai_model = None
        self.client = None
        self.openai_client_type = None
        self.use_ai = False  # Will be set to True if AI model loads successfully
        
        if backend != 'openai':
            logger.warning(f"Only OpenAI is supported. Switching backend '{backend}' to 'openai'.")
        self.backend = 'openai'
        self._init_openai()
        
        # Spam keywords (rule-based) - Hebrew + English
        self.spam_keywords_en = [
            'buy now', 'click here', 'limited time', 'act now',
            'free money', 'earn $$', 'work from home', 'bitcoin',
            'casino', 'viagra', 'pills', 'weight loss',
            'get rich', 'make money fast', 'prize', 'winner',
            'congratulations you won', 'claim your', 'discount code'
        ]
        
        self.spam_keywords_he = [
            'קנה עכשיו', 'לחץ כאן', 'זמן מוגבל', 'פעל עכשיו',
            'כסף חינם', 'הרוויח', 'עבודה מהבית', 'ביטקוין',
            'קזינו', 'הרזיה', 'להרוויח מהר', 'פרס', 'זוכה',
            'מזל טוב זכית', 'קבל את', 'קוד הנחה', 'הטבה מיוחדת'
        ]
        
        # Promotional patterns
        self.promo_patterns = [
            r'https?://\S+\.(tk|ml|ga|cf|gq)',  # Free domains often used for spam
            r'whatsapp\.me/\d+',  # WhatsApp links
            r't\.me/\S+',  # Telegram links
            r'bit\.ly/\S+',  # URL shorteners
            r'\d{10,}',  # Long phone numbers
        ]
    
    def _init_detoxify(self):
        """Initialize Detoxify local model"""
        try:
            from detoxify import Detoxify
            self.ai_model = Detoxify('original')
            logger.info("✅ Detoxify model loaded (English only)")
        except ImportError:
            logger.warning("⚠️ Detoxify not installed. Install: pip install detoxify torch")
            self.ai_model = None
    
    def _init_perspective(self):
        """Initialize Google Perspective API"""
        if not self.api_key:
            logger.warning("⚠️ PERSPECTIVE_API_KEY not set. Get it from: https://perspectiveapi.com/")
            self.backend = 'detoxify'
            self._init_detoxify()
            return
        
        try:
            from googleapiclient import discovery
            self.client = discovery.build(
                "commentanalyzer",
                "v1alpha1",
                developerKey=self.api_key,
                discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
                static_discovery=False,
            )
            logger.info("✅ Google Perspective API initialized (Hebrew + English)")
        except Exception as e:
            logger.error(f"Failed to init Perspective API: {e}")
            logger.warning("Install: pip install google-api-python-client")
            self.backend = 'detoxify'
            self._init_detoxify()
    
    def _init_openai(self):
        """Initialize OpenAI Moderation API"""
        if not self.api_key:
            logger.warning("⚠️ OPENAI_API_KEY not set. Get it from: https://platform.openai.com/api-keys")
            return
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            self.openai_client_type = "new"
            logger.info("✅ OpenAI Moderation API initialized (English only)")
        except ImportError:
            try:
                import openai
                openai.api_key = self.api_key
                self.client = openai
                self.openai_client_type = "legacy"
                logger.info("✅ OpenAI Moderation API initialized (legacy client, English only)")
            except ImportError:
                logger.warning("⚠️ OpenAI not installed. Install: pip install openai")
                self.client = None
    
    def _init_azure(self):
        """Initialize Azure Content Moderator"""
        if not self.api_key:
            logger.warning("⚠️ AZURE_API_KEY not set. Get it from Azure portal")
            self.backend = 'detoxify'
            self._init_detoxify()
            return
        
        endpoint = os.getenv('AZURE_ENDPOINT')
        if not endpoint:
            logger.warning("⚠️ AZURE_ENDPOINT not set")
            self.backend = 'detoxify'
            self._init_detoxify()
            return
        
        try:
            from azure.ai.contentsafety import ContentSafetyClient
            from azure.core.credentials import AzureKeyCredential
            self.client = ContentSafetyClient(endpoint, AzureKeyCredential(self.api_key))
            logger.info("✅ Azure Content Moderator initialized (Hebrew + English)")
        except ImportError:
            logger.warning("⚠️ Azure SDK not installed. Install: pip install azure-ai-contentsafety")
            self.backend = 'detoxify'
            self._init_detoxify()

    
    def check_message(
        self,
        text: str,
        thresholds: Optional[Dict[str, float]] = None
    ) -> ModerationResult:
        """
        Check if message contains problematic content
        
        Args:
            text: Message text to check
            thresholds: Custom thresholds for each category (0.0-1.0)
        
        Returns:
            ModerationResult with flagging decision
        """
        if not text or len(text.strip()) < 3:
            return ModerationResult(
                is_flagged=False,
                violation_type=None,
                confidence=0.0,
                reason="Message too short to analyze",
                scores={}
            )
        
        # Default thresholds
        if thresholds is None:
            thresholds = {
                'toxicity': 0.7,
                'severe_toxicity': 0.5,
                'obscene': 0.7,
                'threat': 0.6,
                'insult': 0.7,
                'identity_hate': 0.6,
                'sexual': 0.7,
                'spam': 0.7,
            }
        
        scores = {}
        
        if self.backend == 'openai' and self.client:
            return self._check_openai(text, thresholds)
        return ModerationResult(
            is_flagged=False,
            violation_type=None,
            confidence=0.0,
            reason="AI backend unavailable",
            scores={}
        )

    @staticmethod
    def _map_content_type(category: str) -> ContentType:
        """Map backend category strings to ContentType enum."""
        mapping = {
            'toxicity': ContentType.TOXIC,
            'severe_toxicity': ContentType.SEVERE_TOXIC,
            'obscene': ContentType.OBSCENE,
            'threat': ContentType.THREAT,
            'insult': ContentType.INSULT,
            'identity_hate': ContentType.IDENTITY_HATE,
            'sexual': ContentType.SEXUAL,
            'sexual_minors': ContentType.SEXUAL,
            'harassment': ContentType.TOXIC,
            'harassment_threatening': ContentType.THREAT,
            'hate': ContentType.IDENTITY_HATE,
            'hate_threatening': ContentType.THREAT,
            'violence': ContentType.THREAT,
            'violence_graphic': ContentType.THREAT,
            'self_harm': ContentType.THREAT,
            'self_harm_intent': ContentType.THREAT,
            'self_harm_instructions': ContentType.THREAT,
            'illicit': ContentType.SPAM,
            'illicit_violent': ContentType.THREAT,
            'spam': ContentType.SPAM,
            'promotion': ContentType.PROMOTION,
        }
        return mapping.get(category, ContentType.TOXIC)
    
    def _check_perspective(self, text: str, thresholds: Dict[str, float]) -> ModerationResult:
        """Check with Google Perspective API (supports Hebrew + English)"""
        try:
            analyze_request = {
                'comment': {'text': text},
                'requestedAttributes': {
                    'TOXICITY': {},
                    'SEVERE_TOXICITY': {},
                    'IDENTITY_ATTACK': {},
                    'INSULT': {},
                    'THREAT': {},
                    'SEXUALLY_EXPLICIT': {}
                },
                'languages': ['he', 'en']  # Hebrew + English
            }
            
            response = self.client.comments().analyze(body=analyze_request).execute()
            
            scores = {
                'toxicity': response['attributeScores']['TOXICITY']['summaryScore']['value'],
                'severe_toxicity': response['attributeScores']['SEVERE_TOXICITY']['summaryScore']['value'],
                'identity_hate': response['attributeScores']['IDENTITY_ATTACK']['summaryScore']['value'],
                'insult': response['attributeScores']['INSULT']['summaryScore']['value'],
                'threat': response['attributeScores']['THREAT']['summaryScore']['value'],
                'sexual': response['attributeScores']['SEXUALLY_EXPLICIT']['summaryScore']['value'],
            }
            
            # Check against thresholds
            for category, score in scores.items():
                threshold = thresholds.get(category, 0.7)
                if score >= threshold:
                    return ModerationResult(
                        is_flagged=True,
                        violation_type=self._map_content_type(category),
                        confidence=score,
                        reason=f"{category.replace('_', ' ').title()} detected (confidence: {score:.1%})",
                        scores=scores
                    )
            
            return ModerationResult(
                is_flagged=False,
                violation_type=None,
                confidence=0.0,
                reason="Content passed moderation",
                scores=scores
            )
        except Exception as e:
            logger.error(f"Perspective API error: {e}")
            return ModerationResult(
                is_flagged=False,
                violation_type=None,
                confidence=0.0,
                reason="Perspective backend error",
                scores={}
            )
    
    def _check_openai(self, text: str, thresholds: Dict[str, float]) -> ModerationResult:
        """Check with OpenAI Moderation API (English only)"""
        try:
            if self.openai_client_type == "new":
                response = self.client.moderations.create(
                    model="omni-moderation-latest",
                    input=text,
                )
                result = response.results[0]
                categories = result.categories
                category_scores = result.category_scores
                flagged = result.flagged
            else:
                response = self.client.Moderation.create(input=text)
                result = response['results'][0]
                categories = result['categories']
                category_scores = result['category_scores']
                flagged = result['flagged']

            def _score(key: str) -> float:
                if isinstance(category_scores, dict):
                    value = category_scores.get(key, 0.0)
                else:
                    attr_name = key.replace('/', '_').replace('-', '_')
                    value = getattr(category_scores, attr_name, 0.0)
                return float(value) if value is not None else 0.0

            def _category_items():
                if isinstance(categories, dict):
                    return categories.items()
                if hasattr(categories, "model_dump"):
                    return categories.model_dump().items()
                if hasattr(categories, "__dict__"):
                    return categories.__dict__.items()
                return []

            raw_keys = [
                'sexual',
                'sexual/minors',
                'harassment',
                'harassment/threatening',
                'hate',
                'hate/threatening',
                'illicit',
                'illicit/violent',
                'self-harm',
                'self-harm/intent',
                'self-harm/instructions',
                'violence',
                'violence/graphic',
            ]

            scores = {
                key.replace('/', '_').replace('-', '_'): _score(key)
                for key in raw_keys
            }

            # Check against thresholds
            for category, score in scores.items():
                threshold = thresholds.get(category, thresholds.get('toxicity', 0.7))
                if score >= threshold:
                    return ModerationResult(
                        is_flagged=True,
                        violation_type=self._map_content_type(category),
                        confidence=score,
                        reason=f"{category.replace('_', ' ').title()} detected (confidence: {score:.1%})",
                        scores=scores
                    )

            if flagged:
                flagged_categories = [
                    k.replace('/', '_').replace('-', '_')
                    for k, v in _category_items() if v
                ]
                return ModerationResult(
                    is_flagged=False,
                    violation_type=None,
                    confidence=max(scores.values()) if scores else 0.0,
                    reason=f"Flagged by backend but below thresholds: {', '.join(flagged_categories)}",
                    scores=scores
                )

            return ModerationResult(
                is_flagged=False,
                violation_type=None,
                confidence=0.0,
                reason="Content passed moderation",
                scores=scores
            )
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return ModerationResult(
                is_flagged=False,
                violation_type=None,
                confidence=0.0,
                reason="OpenAI backend error",
                scores={}
            )
    
    def _check_azure(self, text: str, thresholds: Dict[str, float]) -> ModerationResult:
        """Check with Azure Content Moderator (Hebrew + English)"""
        try:
            from azure.ai.contentsafety.models import TextCategory, AnalyzeTextOptions
            
            request = AnalyzeTextOptions(text=text)
            response = self.client.analyze_text(request)
            
            scores = {
                'hate': response.hate_result.severity / 6.0 if response.hate_result else 0.0,
                'sexual': response.sexual_result.severity / 6.0 if response.sexual_result else 0.0,
                'violence': response.violence_result.severity / 6.0 if response.violence_result else 0.0,
                'self_harm': response.self_harm_result.severity / 6.0 if response.self_harm_result else 0.0,
            }
            
            # Check thresholds
            for category, score in scores.items():
                threshold = thresholds.get(category, 0.7)
                if score >= threshold:
                    return ModerationResult(
                        is_flagged=True,
                        violation_type=ContentType.TOXIC,
                        confidence=score,
                        reason=f"{category.title()} content detected (confidence: {score:.1%})",
                        scores=scores
                    )
            
            return ModerationResult(
                is_flagged=False,
                violation_type=None,
                confidence=0.0,
                reason="Content passed moderation",
                scores=scores
            )
        except Exception as e:
            logger.error(f"Azure API error: {e}")
            return ModerationResult(
                is_flagged=False,
                violation_type=None,
                confidence=0.0,
                reason="Azure backend error",
                scores={}
            )
    
    def _check_detoxify(self, text: str, thresholds: Dict[str, float]) -> ModerationResult:
        """Check with Detoxify local model (English only)"""
        try:
            predictions = self.ai_model.predict(text)
            scores = {
                'toxicity': float(predictions['toxicity']),
                'severe_toxicity': float(predictions['severe_toxicity']),
                'obscene': float(predictions['obscene']),
                'threat': float(predictions['threat']),
                'insult': float(predictions['insult']),
                'identity_hate': float(predictions['identity_attack']),
            }
            
            # Check against thresholds
            for category, score in scores.items():
                threshold = thresholds.get(category, 0.7)
                if score >= threshold:
                    return ModerationResult(
                        is_flagged=True,
                        violation_type=self._map_content_type(category),
                        confidence=score,
                        reason=f"{category.replace('_', ' ').title()} detected (confidence: {score:.1%})",
                        scores=scores
                    )
            
            return ModerationResult(
                is_flagged=False,
                violation_type=None,
                confidence=0.0,
                reason="Content passed moderation",
                scores=scores
            )
        except Exception as e:
            logger.error(f"Detoxify error: {e}")
            return ModerationResult(
                is_flagged=False,
                violation_type=None,
                confidence=0.0,
                reason="Detoxify backend error",
                scores={}
            )
    
    def _check_rules(self, text: str, thresholds: Dict[str, float]) -> ModerationResult:
        """Rule-based checks (fallback - Hebrew + English)"""
        scores = {}
        
        # Check with AI model if available
        if self.use_ai and self.ai_model:
            try:
                predictions = self.ai_model.predict(text)
                scores = {
                    'toxicity': float(predictions['toxicity']),
                    'severe_toxicity': float(predictions['severe_toxicity']),
                    'obscene': float(predictions['obscene']),
                    'threat': float(predictions['threat']),
                    'insult': float(predictions['insult']),
                    'identity_hate': float(predictions['identity_attack']),
                }
                
                # Check against thresholds
                for category, score in scores.items():
                    threshold = thresholds.get(category, 0.7)
                    if score >= threshold:
                        return ModerationResult(
                            is_flagged=True,
                            violation_type=self._map_content_type(category),
                            confidence=score,
                            reason=f"{category.replace('_', ' ').title()} detected (confidence: {score:.1%})",
                            scores=scores
                        )
            except Exception as e:
                logger.error(f"AI moderation error: {e}")
        
        # Rule-based checks (always run as fallback)
        
        # Check for spam
        spam_score = self._check_spam_rules(text)
        scores['spam'] = spam_score
        if spam_score >= thresholds.get('spam', 0.7):
            return ModerationResult(
                is_flagged=True,
                violation_type=ContentType.SPAM,
                confidence=spam_score,
                reason=f"Spam detected (confidence: {spam_score:.1%})",
                scores=scores
            )
        
        # Check for promotional content
        promo_score = self._check_promotion_rules(text)
        scores['promotion'] = promo_score
        if promo_score >= thresholds.get('promotion', 0.7):
            return ModerationResult(
                is_flagged=True,
                violation_type=ContentType.PROMOTION,
                confidence=promo_score,
                reason=f"Promotional content detected (confidence: {promo_score:.1%})",
                scores=scores
            )
        
        # Check for sexual content (basic)
        sexual_score = self._check_sexual_content(text)
        scores['sexual'] = sexual_score
        if sexual_score >= thresholds.get('sexual', 0.7):
            return ModerationResult(
                is_flagged=True,
                violation_type=ContentType.SEXUAL,
                confidence=sexual_score,
                reason=f"Sexual content detected (confidence: {sexual_score:.1%})",
                scores=scores
            )
        
        # No violations found
        return ModerationResult(
            is_flagged=False,
            violation_type=None,
            confidence=0.0,
            reason="Content passed moderation",
            scores=scores
        )
    
    def _check_spam_rules(self, text: str) -> float:
        """Check for spam using rule-based detection (Hebrew + English)"""
        text_lower = text.lower()
        
        # Count spam keyword matches (English + Hebrew)
        matches_en = sum(1 for keyword in self.spam_keywords_en if keyword in text_lower)
        matches_he = sum(1 for keyword in self.spam_keywords_he if keyword in text)
        matches = matches_en + matches_he
        
        # Calculate score based on matches
        if matches == 0:
            return 0.0
        elif matches == 1:
            return 0.5
        elif matches == 2:
            return 0.7
        else:
            return 0.9
    
    def _check_promotion_rules(self, text: str) -> float:
        """Check for promotional content"""
        matches = 0
        
        # Check promotional patterns
        for pattern in self.promo_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matches += 1
        
        # Multiple links = likely promotion
        url_count = len(re.findall(r'https?://\S+', text))
        if url_count >= 3:
            matches += 1
        
        # Excessive caps = likely spam
        if len(text) > 10:
            caps_ratio = sum(1 for c in text if c.isupper()) / len(text)
            if caps_ratio > 0.5:
                matches += 1
        
        # Calculate score
        if matches == 0:
            return 0.0
        elif matches == 1:
            return 0.5
        elif matches == 2:
            return 0.7
        else:
            return 0.9
    
    def _check_sexual_content(self, text: str) -> float:
        """Basic check for sexual content (Hebrew + English)"""
        sexual_keywords_en = [
            'sex', 'porn', 'xxx', 'nude', 'naked', 'nsfw',
            'dick', 'pussy', 'cock', 'fuck', 'cum', 'orgasm'
        ]
        
        sexual_keywords_he = [
            'סקס', 'פורנו', 'עירום', 'עירומים', 'זיון',
            'זין', 'כוס', 'תחת', 'ציצים', 'חשפנות'
        ]
        
        text_lower = text.lower()
        matches_en = sum(1 for keyword in sexual_keywords_en if keyword in text_lower)
        matches_he = sum(1 for keyword in sexual_keywords_he if keyword in text)
        matches = matches_en + matches_he
        
        if matches == 0:
            return 0.0
        elif matches == 1:
            return 0.6
        else:
            return 0.9
    
    def get_supported_categories(self) -> List[str]:
        """Get list of supported moderation categories"""
        if self.backend == 'openai':
            return ['sexual', 'hate', 'violence', 'self_harm']
        return []
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        if self.backend == 'openai':
            return ['en']
        return []


# Singleton instance
_moderator_instance: Optional[ContentModerator] = None


def get_moderator(backend: str = 'openai', api_key: Optional[str] = None) -> ContentModerator:
    """
    Get or create content moderator instance
    
    Args:
        backend: 'openai'
        api_key: OpenAI API key
    """
    global _moderator_instance
    
    if _moderator_instance is None:
        _moderator_instance = ContentModerator(backend=backend, api_key=api_key)
    
    return _moderator_instance
