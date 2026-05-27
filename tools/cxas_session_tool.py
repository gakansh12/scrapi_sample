from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from cxas_scrapi import Agents, Apps, Sessions


@dataclass(frozen=True)
class CxasAgentTarget:
    app_name: str
    agent_name: str | None


def resolve_agent_target(
    *,
    project_id: str,
    location: str,
    app_display_name: str,
    agent_display_name: str | None,
    creds_path: str | None = None,
) -> CxasAgentTarget:
    # CXAS SCRAPI uses full resource names for app_name in Agents/Sessions.
    apps_client = Apps(project_id=project_id, location=location, creds_path=creds_path)
    app = apps_client.get_app_by_display_name(app_display_name)
    if not app:
        raise RuntimeError(
            f"App '{app_display_name}' not found in project '{project_id}' location '{location}'."
        )

    app_name = app.name

    agent_name: str | None = None
    if agent_display_name:
        agents_in_app = Agents(app_name=app_name, creds_path=creds_path)
        agents_map = agents_in_app.get_agents_map(reverse=True)
        agent_name = agents_map.get(agent_display_name)
        if not agent_name:
            raise RuntimeError(f"Agent '{agent_display_name}' not found in app '{app_display_name}'.")

    return CxasAgentTarget(app_name=app_name, agent_name=agent_name)


class CxasVoiceSession:
    def __init__(self, *, app_name: str, creds_path: str | None = None):
        self._sessions = Sessions(app_name=app_name, creds_path=creds_path)
        self.session_id = self._sessions.create_session_id()

    def send_welcome(self, *, caller_id: str) -> Any:
        return self._sessions.run(
            session_id=self.session_id,
            event="WELCOME",
            event_vars={"caller_id": caller_id},
        )

    def send_text(self, text: str, *, variables: dict[str, Any] | None = None) -> Any:
        return self._sessions.run(
            session_id=self.session_id,
            text=text,
            variables=variables,
        )
