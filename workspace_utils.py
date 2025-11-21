import os
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)
WORKSPACE_DIR = "workspace"

if not os.path.exists(WORKSPACE_DIR):
    os.makedirs(WORKSPACE_DIR)

def list_files() -> List[str]:
    try:
        return os.listdir(WORKSPACE_DIR)
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return []

def read_file(filename: str) -> str:
    filepath = os.path.join(WORKSPACE_DIR, filename)
    if not os.path.exists(filepath):
        return "File not found."
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file {filename}: {e}")
        return f"Error reading file: {e}"

def write_file(filename: str, content: str) -> str:
    filepath = os.path.join(WORKSPACE_DIR, filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"File written: {filename}")
        return f"Successfully wrote to {filename}."
    except Exception as e:
        logger.error(f"Error writing file {filename}: {e}")
        return f"Error writing file: {e}"

def append_to_file(filename: str, content: str) -> str:
    filepath = os.path.join(WORKSPACE_DIR, filename)
    try:
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write("\n" + content)
        logger.info(f"Appended to file: {filename}")
        return f"Successfully appended to {filename}."
    except Exception as e:
        logger.error(f"Error appending to file {filename}: {e}")
        return f"Error appending to file: {e}"
