from dataclasses import dataclass
from datetime import datetime
import string


@dataclass
class User:
    username: str
    online: bool
    age: int
    phone_number: str

    @staticmethod
    def validate_username(username: str) -> bool:
        if not username:
            return False

        for char in username:
            if char not in string.ascii_letters and char not in string.digits:
                return False

        return True

    def go_online(self) -> None:
        self.online = True

    def go_offline(self) -> None:
        self.online = False