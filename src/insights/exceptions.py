"""Typed exceptions for iNSIGHTS Research & Intelligence platform.
Ensures clean error classification and user-safe error recovery.
"""

class InsightsError(Exception):
    """Base exception for all iNSIGHTS-related errors."""
    def __init__(self, message: str, user_friendly_message: str = "Research could not be completed at this time."):
        super().__init__(message)
        self.message = message
        self.user_friendly_message = user_friendly_message

class InsightsConfigurationError(InsightsError):
    """Raised when integration settings or environment variables are missing or invalid."""
    def __init__(self, message: str):
        super().__init__(
            message,
            user_friendly_message="Research service is not properly configured. Falling back to local vision."
        )

class InsightsAuthenticationError(InsightsError):
    """Raised when authentication credentials or token are rejected."""
    def __init__(self, message: str = "Authentication failed for iNSIGHTS API"):
        super().__init__(
            message,
            user_friendly_message="Research authentication error. Falling back to local vision."
        )

class InsightsTimeoutError(InsightsError):
    """Raised when the research request times out."""
    def __init__(self, message: str = "iNSIGHTS research request timed out"):
        super().__init__(
            message,
            user_friendly_message="Research took too long to respond. I can still describe what I see."
        )

class InsightsRateLimitError(InsightsError):
    """Raised when rate limits are exceeded."""
    def __init__(self, message: str = "iNSIGHTS rate limit exceeded"):
        super().__init__(
            message,
            user_friendly_message="Research rate limit reached. Using local vision instead."
        )

class InsightsUnavailableError(InsightsError):
    """Raised when the iNSIGHTS platform or endpoint is offline/unreachable."""
    def __init__(self, message: str = "iNSIGHTS service is unavailable"):
        super().__init__(
            message,
            user_friendly_message="Research is temporarily unavailable. I can still describe what I see."
        )

class InsightsResponseError(InsightsError):
    """Raised when the provider returns a malformed or unparseable response."""
    def __init__(self, message: str = "Failed to parse iNSIGHTS research response"):
        super().__init__(
            message,
            user_friendly_message="Received an unclear research response. Summarizing local visual details instead."
        )
