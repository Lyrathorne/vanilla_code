from dataclasses import dataclass
from schemas.users import User
@dataclass
class Message:
    sender: User
    text: str
    timestamp: str

    