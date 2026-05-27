from __future__ import annotations

from config import load_settings
from flow import VoiceSupportFlow
from tools.cxas_session_tool import CxasVoiceSession, resolve_agent_target


def main() -> None:
    settings = load_settings()

    target = resolve_agent_target(
        project_id=settings.project_id,
        location=settings.location,
        app_display_name=settings.app_name,
        agent_display_name=settings.agent_display_name,
        creds_path=settings.creds_path,
    )

    print(f"Using app: {target.app_name}")
    if target.agent_name:
        print(f"Resolved agent: {target.agent_name}")

    session = CxasVoiceSession(app_name=target.app_name, creds_path=settings.creds_path)
    flow = VoiceSupportFlow(session=session)

    print("Starting voice support demo. Type user messages; Ctrl+C to exit.")
    res = flow.start(caller_id="+14155551234")
    print("[WELCOME sent]")

    try:
        while True:
            user_text = input("you> ").strip()
            res = flow.on_user_utterance(user_text)
            # The raw response object is structured; printing it verbatim is noisy.
            # In practice, you'd extract the agent's text output fields.
            print("agent_res(raw)>", type(res).__name__)
    except KeyboardInterrupt:
        print("\nBye")


if __name__ == "__main__":
    main()
