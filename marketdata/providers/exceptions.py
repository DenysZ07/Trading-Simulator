class ProviderError(Exception):
    """Base class for all provider failures."""


class ProviderUnavailable(ProviderError):
    """API is down or connection timed out."""


class SymbolNotFound(ProviderError):
    """Ticker doesn't exist."""


class RateLimited(ProviderError):
    """Too many requests."""