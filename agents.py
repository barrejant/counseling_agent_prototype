import os
from dotenv import load_dotenv
import random
import re
import time
from typing import Dict, List
from openai import OpenAI
import json
import logging

from prompts import get_prompts
from session import SessionManager
from memory_utils import get_embedding, search_memories 
from goal_utils import load_goals, update_sub_goal_status, get_incomplete_goals_text, add_new_task, update_main_goal
from workspace_utils import list_files, read_file, write_file, append_to_file

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
logger = logging.getLogger(__name__)

MEMORY_FILE = "memory_bank.json"
MAX_RETRIES = 3

def call_llm(system_prompt: str, messages: List[Dict[str, str]], model: str = "gpt-4o") -> str:
    api_messages = [{"role": "system", "content": system_prompt}] + messages
    try:
        response = client.chat.completions.create(
            model=model,
            messages=api_messages,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error calling LLM: {e}")
        return "Error: LLM generation failed."

def user_agent(session: SessionManager, language: str = "ja") -> str:
    history = session.get_history()
    prompts = get_prompts(language)
    if not history:
        initial_instruction = "Conversation start..." if language == "en" else "会話の開始です..."
        return call_llm(prompts["USER_AGENT"], [{"role": "user", "content": initial_instruction}])
    return call_llm(prompts["USER_AGENT"], history)

def evaluate_session(session: SessionManager, language: str = "ja") -> str:
    history = session.get_history()
    prompts = get_prompts(language)
    
    trigger_msg = "Now, please evaluate the session. [EVALUATION]" if language == "en" else "セッションを評価してください。[EVALUATION]"
    
    messages = history + [{"role": "system", "content": trigger_msg}]
    
    response = call_llm(prompts["USER_AGENT"], messages)
    return response

def listening_agent(session: SessionManager, language: str = "ja") -> str:
    prompts = get_prompts(language)
    return call_llm(prompts["LISTENING_AGENT"], session.get_history())

def create_and_save_memory(session: SessionManager, language: str = "ja"):
    history = session.get_history()
    session_id = session.session_id
    history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])

    if language == "en":
        memory_prompt = f"Summarize conversation into JSON: {{ 'Current Issue': '...', 'Primary Emotion': '...', 'Barriers Faced': '...' }}\n\n{history_text}"
    else:
        memory_prompt = f"会話をJSONに要約してください: {{ '現在の課題': '...', '主な感情': '...', '直面している障壁': '...' }}\n\n{history_text}"

    for _ in range(MAX_RETRIES):
        try:
            res = call_llm(memory_prompt, [], model="gpt-4o")
            match = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", res)
            json_content = match.group(1) if match else res
            if "{" in json_content:
                json_content = json_content[json_content.find("{"):json_content.rfind("}")+1]
            
            data = json.loads(json_content)
            
            content_text = " ".join([str(v) for k, v in data.items()])
            data["embedding"] = get_embedding(content_text)
            data["session_id"] = session_id
            
            if os.path.exists(MEMORY_FILE) and os.path.getsize(MEMORY_FILE) > 0:
                with open(MEMORY_FILE, 'r', encoding='utf-8') as f: memories = json.load(f)
            else: memories = []
            
            memories.append(data)
            with open(MEMORY_FILE, 'w', encoding='utf-8') as f: json.dump(memories, f, indent=4, ensure_ascii=False)
            logger.info("Memory saved.")
            return
        except: continue

def retrieve_memory(query: str, top_k: int = 1) -> List[Dict]:
    try:
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f: memories = json.load(f)
        return search_memories(query, memories, top_k)
    except: return []

def terminator_agent(session: SessionManager, language: str = "ja") -> str:
    prompts = get_prompts(language)
    return call_llm(prompts["TERMINATOR"], session.get_history())

def goal_agent(session: SessionManager, language: str = "ja") -> str:
    history = session.get_history()
    prompts = get_prompts(language)
    goals_data = load_goals()
    current_main_goal = goals_data.get("main_goal", "未設定")
    incomplete_goals_text = get_incomplete_goals_text()
    
    system_prompt = prompts["GOAL_AGENT"].replace("{incomplete_goals_list}", incomplete_goals_text).replace("{current_main_goal}", current_main_goal)
    
    response_json_str = call_llm(system_prompt, history, model="gpt-4o")
    
    try:
        match = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", response_json_str)
        json_content = match.group(1) if match else response_json_str
        if "{" in json_content:
            json_content = json_content[json_content.find("{"):json_content.rfind("}")+1]

        data = json.loads(json_content)
        if data.get("new_main_goal"): update_main_goal(data.get("new_main_goal"))
        if data.get("completed_goal_id"): update_sub_goal_status(data.get("completed_goal_id"), "complete")
        return data.get("user_message", "Received.")
    except:
        return "目標確認中にエラーが発生しました。"

def action_agent(session: SessionManager, language: str = "ja") -> str:
    history = session.get_history()
    prompts = get_prompts(language)
    
    latest_query = history[-1]['content'] if history else ""
    related_memories = retrieve_memory(latest_query)
    user_goal_data = load_goals()
    main_goal = user_goal_data.get("main_goal", "No goal set.")

    files = list_files()
    current_plan = read_file("plan.md")
    
    if language == "en":
        workspace_context = f"--- Workspace ---\nFiles: {files}\n[plan.md Content]:\n{current_plan}\n"
        memory_context = "--- Memories ---\n" + str([m.get('Current Issue') for m in related_memories])
        goal_context = f"--- Goal ---\n{main_goal}"
    else:
        workspace_context = f"--- Workspace情報 ---\nファイル一覧: {files}\n[plan.md の内容]:\n{current_plan}\n"
        memory_context = "--- 過去の記憶 ---\n" + str([m.get('現在の課題') for m in related_memories])
        goal_context = f"--- 現在の目標 ---\n{main_goal}"

    history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
    
    full_prompt = (
        f"{history_text}\n"
        f"{workspace_context}\n"
        f"{memory_context}\n"
        f"{goal_context}\n"
        f"--- Instruction ---\n{prompts['ACTION_AGENT']}"
    )
    
    for attempt in range(MAX_RETRIES):
        try:
            raw_response = call_llm(full_prompt, messages=[], model="gpt-4o")
            
            match = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", raw_response)
            json_content = match.group(1) if match else raw_response
            if "{" in json_content:
                json_content = json_content[json_content.find("{"):json_content.rfind("}")+1]
            
            data = json.loads(json_content)
            
            file_op = data.get("file_operation")
            op_result = ""
            if file_op and isinstance(file_op, dict):
                fname = file_op.get("filename")
                op = file_op.get("operation")
                content = file_op.get("content", "")
                
                if fname and op and op != "null":
                    if op == "write":
                        op_result = write_file(fname, content)
                    elif op == "append":
                        current_content = read_file(fname)
                        if content.strip() in current_content:
                            op_result = f"Skipped appending to {fname} (Content already exists)."
                        else:
                            op_result = append_to_file(fname, content)
                    elif op == "read":
                        op_result = read_file(fname)
                    
                    if op_result: logger.info(f"Action Agent File Op: {op_result}")

            proposal = data.get('action_proposal', '')
            
            if proposal: add_new_task(proposal)
            
            explanation = data.get('explanation', '')
            if op_result: explanation += f"\n\n(System Log: {op_result})"
            
            return f"**{proposal}**\n\n{explanation}"

        except (json.JSONDecodeError, KeyError):
            continue
            
    return "Action Agent System Error."

def planner_agent(session: SessionManager, language: str = "ja") -> str:
    history = session.get_history()
    prompts = get_prompts(language)
    
    current_plan = read_file("plan.md")
    system_prompt = prompts["PLANNER_AGENT"]
    
    user_context = (
        f"Current Plan (plan.md):\n{current_plan}\n\n"
        f"Conversation History:\n" + "\n".join([f"{m['role']}: {m['content']}" for m in history])
    )
    
    response_json = call_llm(system_prompt, [{"role": "user", "content": user_context}], model="gpt-4o")
    
    try:
        match = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", response_json)
        json_content = match.group(1) if match else response_json
        if "{" in json_content:
            json_content = json_content[json_content.find("{"):json_content.rfind("}")+1]
            
        data = json.loads(json_content)
        thought = data.get("thought_process", "")
        new_plan = data.get("plan_content", "")
        
        if new_plan:
            write_file("plan.md", new_plan)
            logger.info("Planner Agent updated plan.md")
        
        if language == "en":
            return f"**[Plan Updated]**\nThought: {thought}\n\nI have updated `plan.md`. Let's move to the next step."
        else:
            return f"**【計画更新】**\n思考プロセス: {thought}\n\n状況に合わせて `plan.md`（計画書）を更新しました。この方針で進めましょう。"

    except Exception as e:
        logger.error(f"Planner Agent Error: {e}")
        return "Plan update failed."