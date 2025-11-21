from typing import List, Dict

class SessionManager:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.history: List[Dict[str, str]] = []

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})

    def get_history(self) -> List[Dict[str, str]]:
        return self.history

    def clear_history(self):
        self.history = []