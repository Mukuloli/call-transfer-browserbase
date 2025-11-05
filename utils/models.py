"""Data models and state management"""
from dataclasses import dataclass, field
from pydantic import BaseModel

@dataclass
class CallState:
    """Track state of each call"""
    transfer_initiated: bool = False
    negative_sentiment_count: int = 0
    conversation_log: list = field(default_factory=list)
    should_disconnect: bool = False

class AcceptTransfer(BaseModel):
    """Request model for accepting a transfer"""
    transfer_id: str
    agent_name: str