import logging
import random
import time
import argparse
import sys

from session import SessionManager

from agents import (
    user_agent, 
    listening_agent, 
    action_agent, 
    terminator_agent,
    goal_agent,      
    planner_agent,   
    evaluate_session, 
    create_and_save_memory
)
from orchestrator import orchestrator
from workspace_utils import read_file

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("simulation.log", mode='a', encoding='utf-8'), 
        logging.StreamHandler()
    ]
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

MAX_TURNS = 15

def run_simulation(interactive: bool, language: str):
    """
    シミュレーションまたは対話セッションを実行するメイン関数
    """
    session_id = f"sim_{time.strftime('%Y%m%d_%H%M%S')}_{random.randint(100, 999)}"
    mode_str = "Interactive (Human)" if interactive else "Simulation (AI User)"
    
    start_msg = f"--- Session Start: {session_id} | Mode: {mode_str} | Lang: {language} ---"
    logger.info(start_msg)
    
    if interactive:
        print(f"\n{start_msg}")
        print("Type 'exit' or 'quit' to end the session manually.\n")

    session = SessionManager(session_id)
    
    if interactive:
        print("Agent: (Waiting for your input...)")
        try:
            user_msg = input("You: ")
        except KeyboardInterrupt:
            print("\nSession interrupted.")
            return
    else:
        user_msg = user_agent(session, language=language)
        logger.info(f"User (Sim): {user_msg}")

    session.add_message("user", user_msg)

    for turn in range(MAX_TURNS):
        if turn >= MAX_TURNS - 1:
            logger.info("Max turns reached.")
            break
            
        route = orchestrator(session, language=language)
        
        if route == "LISTENING":
            agent_msg = listening_agent(session, language=language)
        
        elif route == "ACTION":
            agent_msg = action_agent(session, language=language)
        
        elif route == "GOAL":
            agent_msg = goal_agent(session, language=language)
            if interactive:
                print("\n🎉 CONGRATULATIONS! 🎉\n")
        
        elif route == "PLANNER":
            agent_msg = planner_agent(session, language=language)
            current_plan = read_file("plan.md")
            if current_plan and current_plan != "File not found.":
                plan_display = f"\n--- [Current Plan] ---\n{current_plan}\n----------------------"
                if interactive:
                    print(plan_display)
                else:
                    logger.info(plan_display)
        
        elif route == "TERMINATOR":
            agent_msg = terminator_agent(session, language=language)
        
        else:
            agent_msg = "Error: Unknown Route."

        session.add_message("assistant", agent_msg)

        if interactive:
            print(f"\nAgent ({route}): {agent_msg}\n")
            logger.info(f"Agent ({route}): {agent_msg}")
        else:
            logger.info(f"Agent ({route}): {agent_msg}")

        if route == "TERMINATOR":
            logger.info("Terminator agent triggered. Ending session.")
            break
        
        if interactive:
            try:
                user_msg = input("You: ")
                if user_msg.strip().lower() in ["exit", "quit"]:
                    print("User requested exit.")
                    break
            except KeyboardInterrupt:
                print("\nSession interrupted.")
                break
        else:
            user_msg = user_agent(session, language=language)
            logger.info(f"User (Sim): {user_msg}")
        
        session.add_message("user", user_msg)
    
    logger.info("--- Evaluation Phase ---")
    
    create_and_save_memory(session, language=language)
    
    if not interactive:
        evaluation_result = evaluate_session(session, language=language)
        logger.info(f"Final Evaluation:\n{evaluation_result}")
    
    logger.info(f"--- Session End: {session_id} ---\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Counseling Agent 2.0")
    
    parser.add_argument(
        "--interactive", "-i", 
        action="store_true", 
        help="Run in interactive mode (Human input)."
    )
    
    parser.add_argument(
        "--lang", "-l", 
        type=str, 
        default="ja", 
        choices=["ja", "en"], 
        help="Language setting (ja/en)."
    )
    
    args = parser.parse_args()
    
    run_simulation(interactive=args.interactive, language=args.lang)