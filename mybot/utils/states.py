# Управление состояниями
from typing import Dict, Optional

user_states: Dict[str, str] = {}
user_current_subject: Dict[str, str] = {}

def set_state(user_id: str, state: str) -> None:
    user_states[str(user_id)] = state

def get_state(user_id: str) -> Optional[str]:
    return user_states.get(str(user_id))

def clear_state(user_id: str) -> None:
    if str(user_id) in user_states:
        del user_states[str(user_id)]

def set_current_subject(user_id: str, subject: str) -> None:
    user_current_subject[str(user_id)] = subject

def get_current_subject(user_id: str) -> Optional[str]:
    return user_current_subject.get(str(user_id))