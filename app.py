import streamlit as st
import time
import random
import os
from dotenv import load_dotenv

from session import SessionManager
from agents import (
    listening_agent, 
    action_agent, 
    terminator_agent, 
    goal_agent, 
    planner_agent, 
    create_and_save_memory
)
from orchestrator import orchestrator
from goal_utils import load_goals
from workspace_utils import read_file

load_dotenv()

st.set_page_config(page_title="AI Counseling Agent 2.0", page_icon="🌿")
st.title("🌿 AI Counseling Agent 2.0")

with st.sidebar:
    st.header("Settings")
    language = st.radio("Language / 言語", ["ja", "en"], index=0)
    
    if st.button("Clear Conversation"):
        st.session_state.session_manager = SessionManager(f"web_{int(time.time())}")
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    if language == "en":
        todo_header = "📝 To-Do List"
        main_goal_label = "Main Goal"
        tasks_label = "Micro Steps"
        no_task_msg = "No tasks yet."
    else:
        todo_header = "📝 To-Do リスト"
        main_goal_label = "長期目標"
        tasks_label = "今のスモールステップ"
        no_task_msg = "タスクはまだありません。"

    st.header(todo_header)
    goal_data = load_goals()
    
    st.caption(f"▼ {main_goal_label}")
    st.info(goal_data.get("main_goal", "Unset"))

    st.caption(f"▼ {tasks_label}")
    sub_goals = goal_data.get("sub_goals", [])
    if not sub_goals:
        st.write(f"*{no_task_msg}*")
    else:
        for sg in sub_goals:
            icon = "✅" if sg["status"] == "complete" else "⬜"
            st.write(f"{icon} {sg['name']}")

if "session_manager" not in st.session_state:
    session_id = f"web_{int(time.time())}_{random.randint(100, 999)}"
    st.session_state.session_manager = SessionManager(session_id)

if "messages" not in st.session_state:
    st.session_state.messages = []
    initial_msg = "こんにちは。何でも話してください。" if language == "ja" else "Hello. I'm here to help."
    st.session_state.messages.append({"role": "assistant", "content": initial_msg})
    st.session_state.session_manager.add_message("assistant", initial_msg)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("Input here..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.session_manager.add_message("user", user_input)

    with st.chat_message("assistant"):
        with st.spinner("Agents are thinking..."):
            route = orchestrator(st.session_state.session_manager, language=language)
            
            with st.expander(f"Debug Info: {route}"):
                st.text(f"Selected Agent: {route}")
            
            if route == "LISTENING":
                response = listening_agent(st.session_state.session_manager, language=language)
            elif route == "ACTION":
                response = action_agent(st.session_state.session_manager, language=language)
            elif route == "GOAL":
                response = goal_agent(st.session_state.session_manager, language=language)
                st.balloons()
            elif route == "PLANNER":
                response = planner_agent(st.session_state.session_manager, language=language)
                updated_plan = read_file("plan.md")
                with st.expander("📄 Updated Plan (plan.md)"):
                    st.markdown(updated_plan)
            elif route == "TERMINATOR":
                response = terminator_agent(st.session_state.session_manager, language=language)
                create_and_save_memory(st.session_state.session_manager, language=language)
                st.toast("Session Memory Saved!", icon="💾")
            else:
                response = "System Error."

            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.session_manager.add_message("assistant", response)