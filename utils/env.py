import os
from dotenv import load_dotenv

load_dotenv()

DEFAULTS = {
    "COLLECTION_BASE_PATH": "./",
}


def get_env(key: str) -> str:
    """
    Get environment variable. Fallback to DEFAULTS if missing
    """

    return os.getenv(key, DEFAULTS.get(key, ""))
