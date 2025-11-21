import os
import logging
from openai import OpenAI
from typing import List, Dict
from session import SessionManager
from prompts import get_prompts
from dotenv import load_dotenv
from workspace_utils import read_file

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
logger = logging.getLogger(__name__)

def call_llm(system_prompt: str, messages: List[Dict[str, str]], model: str = "gpt-4o") -> str:
    api_messages = [{"role": "system", "content": system_prompt}] + messages
    try:
        response = client.chat.completions.create(
            model=model,
            messages=api_messages,
            temperature=0.0,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error calling LLM in Orchestrator: {e}")
        return "ERROR_FALLBACK"

def orchestrator(session: SessionManager, language: str = "ja") -> str:
    history = session.get_history()
    if not history: return "LISTENING"

    listening_sequence = 0
    if language == "en":
        listening_keywords = ["feel", "understand", "hear you", "sounds like", "hard", "difficult"]
    else:
        listening_keywords = ["不安", "辛い", "いるんですね", "そうなんですね", "感じて"]

    for message in reversed(history):
        if message['role'] == 'assistant':
            content = message['content']
            if any(keyword in content for keyword in listening_keywords):
                 listening_sequence += 1
            else: break 

    current_plan = read_file("plan.md")
    has_plan = False
    if current_plan and current_plan != "File not found." and len(current_plan) > 10:
        has_plan = True

    if has_plan and listening_sequence >= 1:
        logger.info(f"Orchestrator: Forced Routing -> ACTION (Plan exists + Listening sequence detected)")
        return "ACTION"

    if not has_plan and listening_sequence >= 4:
        logger.info(f"Orchestrator: Forced Routing -> TERMINATOR (Negative Loop without Plan)")
        return "TERMINATOR"
    
    prompts = get_prompts(language)
    base_prompt = prompts["ORCHESTRATOR"]
    
    plan_status_str = "Yes" if has_plan else "No"
    if language == "en":
        context_injection = f"\n[Context Info]\nPlan Exists: {plan_status_str}\nIMPORTANT: If Plan Exists, prioritize 'ACTION' even if the user is anxious. Action cures anxiety.\n"
    else:
        context_injection = f"\n【コンテキスト情報】\n計画書(plan.md)の有無: {plan_status_str}\n重要: 計画書が存在する場合は、ユーザーが不安がっていても『ACTION』を優先してください。小さな行動こそが不安を解消します。\n"

    system_prompt = base_prompt + context_injection
    
    raw_response = call_llm(system_prompt, history, model="gpt-4o")
    decision = raw_response.upper().replace(" ", "").strip()

    logger.info(f"Orchestrator Logic: HasPlan={has_plan}, Decision={decision}")

    if "PLANNER" in decision: return "PLANNER"
    elif "GOAL" in decision: return "GOAL"
    elif "ACTION" in decision: return "ACTION"
    elif "LISTENING" in decision: return "LISTENING"
    elif "TERMINATOR" in decision: return "TERMINATOR"
    else: return "LISTENING"