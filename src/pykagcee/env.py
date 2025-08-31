from typing import Final, Optional
from dotenv import dotenv_values
import os

config = {
    **dotenv_values(".env"),
    **os.environ,
}

NEO4J_URI: Final[Optional[str]] = config.get("NEO4J_URI")
NEO4J_USERNAME: Final[Optional[str]] = config.get("NEO4J_USERNAME")
NEO4J_PASSWORD: Final[Optional[str]] = config.get("NEO4J_PASSWORD")
