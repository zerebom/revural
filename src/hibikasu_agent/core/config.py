from __future__ import annotations

import os

try:
    # Best-effort: load .env if present for local dev
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


class Settings:
    """Application settings centralized in one place.

    This implementation avoids introducing new dependencies (pydantic-settings)
    while providing a simple, explicit configuration surface.
    """

    def __init__(
        self,
        *,
        cors_allow_origins: str | None | list[str] = None,
        cors_allow_origin_regex: str | None = None,
        hibikasu_log_level: str = "INFO",
    ) -> None:
        # Accept both CSV string and list for flexibility
        if isinstance(cors_allow_origins, str):
            self._cors_allow_origins_raw = cors_allow_origins
            self._cors_allow_origins_list = [o.strip() for o in cors_allow_origins.split(",") if o.strip()]
        elif isinstance(cors_allow_origins, list):
            self._cors_allow_origins_raw = ",".join(cors_allow_origins)
            self._cors_allow_origins_list = cors_allow_origins
        else:
            self._cors_allow_origins_raw = None
            self._cors_allow_origins_list = None

        self.cors_allow_origin_regex = cors_allow_origin_regex
        self.hibikasu_log_level = hibikasu_log_level

    @property
    def cors_allow_origins(self) -> list[str]:
        """Resolved list of allowed origins for CORS.

        Defaults include common local dev ports (Next.js/Vite) when unset.
        """
        if self._cors_allow_origins_list is not None:
            return self._cors_allow_origins_list
        return [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]

    @property
    def cors_allow_origin_regex_or_none(self) -> str | None:
        return self.cors_allow_origin_regex or None

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            cors_allow_origins=os.getenv("CORS_ALLOW_ORIGINS"),
            cors_allow_origin_regex=os.getenv("CORS_ALLOW_ORIGIN_REGEX"),
            hibikasu_log_level=os.getenv("HIBIKASU_LOG_LEVEL", "INFO"),
        )


# Singleton settings instance for application-wide use
settings = Settings.from_env()
