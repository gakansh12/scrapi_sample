from __future__ import annotations

from pydantic import BaseModel
from dotenv import load_dotenv
import os


class Settings(BaseModel):
    project_id: str
    location: str = "global"
    app_name: str
    agent_display_name: str | None = None
    creds_path: str | None = None


def load_settings() -> Settings:
    load_dotenv()

    project_id = os.getenv("GCP_PROJECT_ID", "").strip()
    app_name = os.getenv("CXAS_APP_NAME", "").strip()

    if not project_id:
        raise RuntimeError("Missing env var GCP_PROJECT_ID")
    if not app_name:
        raise RuntimeError("Missing env var CXAS_APP_NAME")

    return Settings(
        project_id=project_id,
        location=os.getenv("GCP_LOCATION", "global").strip() or "global",
        app_name=app_name,
        agent_display_name=(os.getenv("CXAS_AGENT_DISPLAY_NAME") or "").strip() or None,
        creds_path=(os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or "").strip() or None,
    )
