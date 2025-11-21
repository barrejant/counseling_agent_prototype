import json
import logging
import os
from typing import List, Dict, Any

logger = logging.getLogger(__name__)
GOALS_FILE = "goals.json"

def load_goals() -> Dict[str, Any]:
    try:
        with open(GOALS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"main_goal": "未設定", "sub_goals": []}

def save_goals(data: Dict[str, Any]):
    with open(GOALS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def update_sub_goal_status(sub_goal_id: int, status: str) -> bool:
    data = load_goals()
    updated = False
    for sg in data.get("sub_goals", []):
        if sg["id"] == sub_goal_id:
            sg["status"] = status
            updated = True
            break
    if updated:
        save_goals(data)
        logger.info(f"Goal ID {sub_goal_id} status updated to '{status}'.")
    else:
        logger.warning(f"Goal ID {sub_goal_id} not found.")
    return updated

def get_incomplete_goals_text() -> str:
    data = load_goals()
    text = ""
    for sg in data.get("sub_goals", []):
        if sg.get("status") != "complete":
            text += f"- ID {sg['id']}: {sg['name']}\n"
    return text if text else "なし"

def add_new_task(task_name: str):
    data = load_goals()
    sub_goals = data.get("sub_goals", [])
    if sub_goals:
        new_id = max(g["id"] for g in sub_goals) + 1
    else:
        new_id = 1
    new_task = {"id": new_id, "name": task_name, "status": "incomplete"}
    sub_goals.append(new_task)
    data["sub_goals"] = sub_goals
    save_goals(data)
    logger.info(f"New task added: {task_name} (ID: {new_id})")
    return new_id

def update_main_goal(new_goal_text: str):
    data = load_goals()
    old_goal = data.get("main_goal", "")
    data["main_goal"] = new_goal_text
    save_goals(data)
    logger.info(f"Main goal updated: '{old_goal}' -> '{new_goal_text}'")
    return True