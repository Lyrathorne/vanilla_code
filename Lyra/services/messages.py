def preview(self) -> str:
        return f"{self.text[:10]} - {self.sender.username}"

def __str__(self) -> str:
        return f"[{self.timestamp}] {self.sender.username}: {self.text}"