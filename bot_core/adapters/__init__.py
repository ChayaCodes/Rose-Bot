from .base_adapter import BotAdapter

# Import platform adapters only if their dependencies are available
try:
    from .telegram_adapter import TelegramAdapter
    TELEGRAM_AVAILABLE = True
except ImportError:
    TelegramAdapter = None
    TELEGRAM_AVAILABLE = False

try:
    from .whatsapp_adapter import WhatsAppAdapter
    WHATSAPP_AVAILABLE = True
except ImportError:
    WhatsAppAdapter = None
    WHATSAPP_AVAILABLE = False

__all__ = ['BotAdapter', 'TelegramAdapter', 'WhatsAppAdapter', 'TELEGRAM_AVAILABLE', 'WHATSAPP_AVAILABLE']
