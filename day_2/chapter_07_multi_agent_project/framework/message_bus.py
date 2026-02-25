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
        - export_to_markdown() to dump the full log to a readable .md file
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

    def export_to_markdown(self, file_path: str) -> str:
        """
        Export the full message history to a readable markdown file.

        Args:
            file_path: Path to the output .md file.

        Returns:
            The file path written.
        """
        lines = [
            "# 📬 Message Bus Log",
            "",
            f"> Total messages: {len(self._messages)}",
            "",
            "---",
            "",
        ]

        for i, msg in enumerate(self._messages, 1):
            # Header with direction arrow
            lines.append(f"## Message {i}: {msg.sender} → {msg.receiver}")
            lines.append("")
            lines.append(f"| Field | Value |")
            lines.append(f"|-------|-------|")
            lines.append(f"| **Type** | `{msg.msg_type}` |")
            lines.append(f"| **Timestamp** | `{msg.timestamp}` |")

            if msg.metadata:
                meta_str = ", ".join(f"{k}={v}" for k, v in msg.metadata.items())
                lines.append(f"| **Metadata** | {meta_str} |")

            lines.append("")
            lines.append("**Content:**")
            lines.append("")

            content_str = str(msg.content)
            # If content looks like markdown, keep it as-is; otherwise wrap in code block
            if content_str.startswith("#") or content_str.startswith("-") or "**" in content_str:
                lines.append(content_str)
            else:
                lines.append("```")
                lines.append(content_str[:3000])  # Cap very long content
                if len(content_str) > 3000:
                    lines.append(f"... (truncated, {len(content_str)} chars total)")
                lines.append("```")

            lines.append("")
            lines.append("---")
            lines.append("")

        # Write to file
        import os
        os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return file_path

    def __len__(self):
        return len(self._messages)
