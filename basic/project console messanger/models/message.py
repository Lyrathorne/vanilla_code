from dataclasses import dataclass
from datetime import datetime
import string
from models.user import User
@dataclass
class Message:
    sender: User
    text: str
    timestamp: str

    def preview(self) -> str:
        return f"{self.text[:10]} - {self.sender.username}"

    def __str__(self) -> str:
        return f"[{self.timestamp}] {self.sender.username}: {self.text}"