"""
Framework: Message Bus
========================
Structured inter-agent communication.

The MessageBus is a simple publish/subscribe system that lets agents
pass structured messages (tasks, results, documents) between each other
without being tightly coupled.

This is essential for the multi-agent workflow:
    Clarifier → PRD Agent → Planner → Coder
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Message:
    """A structured message between agents."""
    sender: str
    receiver: str
    msg_type: str           # e.g. "task", "result", "document", "feedback"
    content: Any            # The payload (string, dict, list, etc.)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: dict = field(default_factory=dict)

    def __repr__(self):
        preview = str(self.content)[:80]
        return f"Message({self.sender}→{self.receiver}, type={self.msg_type}, content={preview!r})"


class MessageBus:
    """
    A simple message bus for inter-agent communication.

    Agents can:
        - send() a message to a specific receiver
        - receive() all messages addressed to them
        - get_conversation() to see the full history between two agents
    """

    def __init__(self):
        self._messages: list[Message] = []

    def send(
        self,
        sender: str,
        receiver: str,
        msg_type: str,
        content: Any,
        metadata: dict | None = None,
    ) -> Message:
        """
        Send a message from one agent to another.

        Args:
            sender:   Name of the sending agent.
            receiver: Name of the receiving agent.
            msg_type: Type of message (e.g. "task", "result", "document").
            content:  The message payload.
            metadata: Optional extra data.

        Returns:
            The created Message.
        """
        msg = Message(
            sender=sender,
            receiver=receiver,
            msg_type=msg_type,
            content=content,
            metadata=metadata or {},
        )
        self._messages.append(msg)
        return msg

    def receive(self, receiver: str, msg_type: str | None = None) -> list[Message]:
        """
        Get all messages for a given receiver.

        Args:
            receiver: The agent name to get messages for.
            msg_type: Optional filter by message type.

        Returns:
            List of messages, oldest first.
        """
        msgs = [m for m in self._messages if m.receiver == receiver]
        if msg_type:
            msgs = [m for m in msgs if m.msg_type == msg_type]
        return msgs

    def get_latest(self, receiver: str, msg_type: str | None = None) -> Message | None:
        """Get the most recent message for a receiver."""
        msgs = self.receive(receiver, msg_type)
        return msgs[-1] if msgs else None

    def get_conversation(self, agent_a: str, agent_b: str) -> list[Message]:
        """Get all messages exchanged between two agents."""
        return [
            m for m in self._messages
            if (m.sender == agent_a and m.receiver == agent_b)
            or (m.sender == agent_b and m.receiver == agent_a)
        ]

    def get_all(self) -> list[Message]:
        """Get the complete message history."""
        return list(self._messages)

    def clear(self):
        """Clear all messages."""
        self._messages.clear()

    def __len__(self):
        return len(self._messages)
