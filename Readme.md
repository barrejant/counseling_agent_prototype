# AI Counseling Agent (Agents 2.0 Architecture) 🌿

**A Multi-Agent AI System for Behavioral Change Support.**
*Available in Japanese (ja) and English (en).*

This project implements an advanced AI agent designed to help users overcome "Analysis Paralysis" and anxiety. Unlike traditional chatbots, it utilizes the **Agents 2.0 Architecture** to explicitly plan, execute file operations, and proactively guide the user toward action.

## 🚀 Agents 2.0 Capabilities

This system goes beyond a simple conversation loop ("Agent 1.0") by incorporating:

* **🧠 Explicit Planning (The Planner)**: A specialized Planner Agent autonomously creates and updates a structured plan (`workspace/plan.md`) based on the user's vague goals.
* **📂 Persistent Workspace**: Agents have read/write access to a local file system to create deliverables (To-Do lists, drafts) that persist beyond the context window.
* **⚡ Deep Orchestration**: The Orchestrator enforces a "bias for action." If a plan exists, it intervenes to stop excessive empathy loops and forces the execution of micro-steps to cure anxiety.
* **📚 RAG Long-term Memory**: Uses Vector Search to recall past successful strategies and emotional states.

## ⚠️ Model Requirement

**This system is hardcoded to use OpenAI's `gpt-4o` model.**

* The complex routing logic and JSON output stability required for the "Agents 2.0" architecture rely on the reasoning capabilities of GPT-4o.
* Please ensure your OpenAI API Key has access to `gpt-4o`.
* *Note: You can modify `call_llm` in `agents.py` if you wish to experiment with other models (e.g., `gpt-4o-mini`), but performance may vary.*

## 🌍 Language Support

* **Japanese (`ja`)**: Default. Optimized for high-context cultural nuances.
* **English (`en`)**: Fully translated prompts and logic.

## 📂 File Structure

* **Core Logic**
    * `main.py`: CLI entry point.
    * `app.py`: **Streamlit Web UI** entry point (Recommended).
    * `orchestrator.py`: Deep routing logic with state awareness.
* **Agents**
    * `agents.py`: Implementations of User, Listening, Action, Goal, and Planner agents.
    * `prompts.py`: System prompts (JA/EN).
* **Utilities**
    * `memory_utils.py`: RAG / Vector Search logic.
    * `goal_utils.py`: JSON-based goal tracking.
    * `workspace_utils.py`: File system operations for Agents.
    * `session.py`: Session state management.

## 🚀 Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/barrejant/counseling_agent_prototype.git
    cd counseling_agent_prototype
    ```

2.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Setup Environment**
    Create a `.env` file in the root directory and add your API key:
    ```text
    OPENAI_API_KEY=sk-your-api-key...
    ```

## 📖 Usage

### 1. Web UI Mode (Recommended)
Run the interactive chat interface in your browser.
```bash
streamlit run app.py
```
*Access the UI at `http://localhost:8501`.*

### 2. CLI Mode (Developer/Debug)
You can run the agent directly in your terminal using `main.py`.

**Command Line Arguments:**
* `-i`, `--interactive`: Run in **Interactive Mode** (Human vs AI). If omitted, it runs in **Simulation Mode** (AI vs AI).
* `-l`, `--lang`: Set language. Options: `ja` (default), `en`.

**Examples:**

* **Talk to the Agent (Japanese)** - *Start here!*
    ```bash
    python main.py -i
    ```

* **Talk to the Agent (English)**
    ```bash
    python main.py -i --lang en
    ```

* **Run Simulation (AI User vs AI Agent)**
    Watch the agents interact with each other automatically.
    ```bash
    python main.py
    ```

## 🛠 Technologies

* **Python 3.10+**
* **OpenAI API** (Hardcoded: `gpt-4o` for logic, `text-embedding-3-small` for RAG)
* **Streamlit**
* **NumPy**

## 👤 Author

**Daichi Kohmoto**
* Github: [@barrejant](https://github.com/barrejant)

## 📚 Citation

If you use this code for your research, please cite it as follows:

```bibtex
@misc{ai_counseling_agent,
  author = {Daichi Kohmoto},
  title = {AI Counseling Agent: An Agents 2.0 Implementation for Behavioral Change},
  year = {2025},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{[https://github.com/](https://github.com/)[YourUsername]/[RepoName]}}
}
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
