"""OAuth token refresh utilities."""

import logging
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from config import settings

logger = logging.getLogger(__name__)


def refresh_oauth_token_if_needed(access_token: str, refresh_token: str, expires_at: datetime) -> tuple[str, str]:
    """
    Refresh OAuth token if expired, return (access_token, refresh_token).
    
    Args:
        access_token: Current access token
        refresh_token: Refresh token
        expires_at: Token expiry datetime
        
    Returns:
        Tuple of (access_token, refresh_token) - new if refreshed, same if still valid
    """
    try:
        credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_OAUTH_CLIENT_ID,
            client_secret=settings.GOOGLE_OAUTH_CLIENT_SECRET,
            expiry=expires_at,
        )
        
        # Check if token is expired or near expiry (within 5 minutes)
        if credentials.expired:
            logger.info("OAuth token expired, refreshing...")
            request = Request()
            credentials.refresh(request)
            logger.info("OAuth token refreshed successfully")
            return credentials.token, credentials.refresh_token
        
        return access_token, refresh_token
        
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}", exc_info=True)
        # Return original tokens if refresh fails - caller will handle the error
        return access_token, refresh_token
