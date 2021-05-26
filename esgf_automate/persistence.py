

from typing import Dict, Optional, Tuple

from globus_action_provider_tools import ActionRequest, ActionStatus


DB_ENTRY_TYPE = Tuple[Optional[ActionStatus], Optional[ActionRequest], Optional[Dict]]

_fake_db: Dict[str, DB_ENTRY_TYPE] = {}

def store_action(action: ActionStatus, request: ActionRequest, extra_info: Optional[Dict] = None):
    action_id = action.action_id
    _fake_db[action_id] = (action, request, extra_info)

def lookup_action_by_id(action_id: str) -> DB_ENTRY_TYPE:
    if action_id in _fake_db:
        return _fake_db[action_id]
    else:
        return (None, None, None)

def delete_action_by_id(action_id: str):
    _fake_db.pop(action_id, False)
