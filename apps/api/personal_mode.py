"""Personal mode utilities for single-user operation."""

from config import settings

def is_personal() -> bool:
    """Check if the app is running in personal mode."""
    return settings.FORGEOS_MODE == "personal"

# Hardcoded personal user and organization IDs (used only in personal mode)
PERSONAL_USER_ID = "aaron"
PERSONAL_ORG_ID = "personal"
PERSONAL_ORG_NAME = "Personal"
PERSONAL_USER_ROLE = "owner"
