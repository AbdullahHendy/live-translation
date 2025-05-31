# live_translation/__init__.py

from .server.server import LiveTranslationServer
from .server.config import Config as ServerConfig
from .client.client import LiveTranslationClient
from .client.config import Config as ClientConfig

__all__ = [
    "LiveTranslationServer",
    "ServerConfig",
    "LiveTranslationClient",
    "ClientConfig",
]

__version__ = "0.7.0"
