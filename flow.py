from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from tools.cxas_session_tool import CxasVoiceSession


class FlowState(str, Enum):
    GREETING = "GREETING"
    VERIFYING = "VERIFYING"
    ROUTING = "ROUTING"
    RESOLVING = "RESOLVING"
    CLOSING = "CLOSING"


@dataclass
class CallContext:
    caller_id: str
    verified_name: str | None = None
    last_intent_hint: str | None = None


class VoiceSupportFlow:
    def __init__(self, *, session: CxasVoiceSession):
        self._session = session
        self.state: FlowState = FlowState.GREETING
        self.ctx: CallContext | None = None

    def start(self, *, caller_id: str) -> Any:
        self.ctx = CallContext(caller_id=caller_id)
        self.state = FlowState.GREETING
        return self._session.send_welcome(caller_id=caller_id)

    def on_user_utterance(self, text: str) -> Any:
        if not self.ctx:
            raise RuntimeError("Flow not started")

        text = (text or "").strip()
        if not text:
            return self._session.send_text("Sorry, I didn’t catch that. How can I help?")

        if self.state == FlowState.GREETING:
            self.state = FlowState.VERIFYING
            return self._session.send_text(
                "Thanks. Before we begin, what’s the name on the account?"
            )

        if self.state == FlowState.VERIFYING:
            self.ctx.verified_name = text
            self.state = FlowState.ROUTING
            return self._session.send_text(
                f"Thanks, {text}. What can I help you with today? (billing, claims, coverage, or other)"
            )

        if self.state == FlowState.ROUTING:
            self.ctx.last_intent_hint = self._classify_intent_hint(text)
            self.state = FlowState.RESOLVING
            return self._session.send_text(
                text,
                variables={
                    "caller_id": self.ctx.caller_id,
                    "verified_name": self.ctx.verified_name,
                    "intent_hint": self.ctx.last_intent_hint,
                },
            )

        if self.state == FlowState.RESOLVING:
            if self._is_goodbye(text):
                self.state = FlowState.CLOSING
                return self._session.send_text(
                    "Thanks for calling. If you need anything else, just say 'agent' or call back. Goodbye."
                )

            return self._session.send_text(
                text,
                variables={
                    "caller_id": self.ctx.caller_id,
                    "verified_name": self.ctx.verified_name,
                    "intent_hint": self.ctx.last_intent_hint,
                },
            )

        return self._session.send_text("Goodbye.")

    @staticmethod
    def _is_goodbye(text: str) -> bool:
        t = text.lower()
        return any(p in t for p in ["bye", "goodbye", "that’s all", "thats all", "no thanks"])

    @staticmethod
    def _classify_intent_hint(text: str) -> str:
        t = text.lower()
        if any(k in t for k in ["bill", "payment", "balance", "invoice"]):
            return "billing"
        if any(k in t for k in ["claim", "denial", "reimbursement"]):
            return "claims"
        if any(k in t for k in ["coverage", "benefit", "eligible", "copay", "deductible"]):
            return "coverage"
        if any(k in t for k in ["agent", "representative", "human"]):
            return "transfer"
        return "general"
