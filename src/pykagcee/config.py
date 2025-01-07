from typing import Final
from dotenv import dotenv_values

env_vars = dotenv_values(".env")


def env(key: str, default: str = None) -> str:
    value = env_vars.get(key)

    if value is not None:
        return value

    if default is not None:
        return default

    raise ValueError(f"Environment variable '{key}' not found")


NEO4J_URI: Final = env("NEO4J_URI")

NEO4J_USERNAME: Final = env("NEO4J_USERNAME")

NEO4J_PASSWORD: Final = env("NEO4J_PASSWORD")
