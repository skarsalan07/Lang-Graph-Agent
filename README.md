# Lang-Graph-Agent
# LangGraph Customer Support Agent

This is a stage-based Customer Support Agent implemented using [LangGraph](https://github.com/langchain-ai/langgraph).
It models **11 workflow stages** (Intake → Complete), orchestrates between abilities via **MCP Clients** (COMMON vs ATLAS), and
demonstrates **state persistence**, **deterministic sequences**, and **non-deterministic orchestration**.

---

## 🎯 Features
- Graph-based orchestration with **LangGraph**
- **Deterministic stages** executed sequentially
- **Non-deterministic reasoning** (DECIDE stage with score-based branching)
- **MCP Client abstraction**:
  - COMMON server = internal / local abilities
  - ATLAS server = external / LLM / DB interactions
- Logs every stage and ability execution
- Outputs a structured final payload

---

## 📂 Repository Structure
- `agent.py` → Main agent code (graph definition, 11 stage functions, demo runner).
- `config.yaml` → Stage configuration (mode, abilities, MCP mapping).
- `demo_run.md` → Example input, logs, and output payload.

---

## 🚀 Installation
```bash
git clone <your_repo_link>
cd langgraph-support-agent
pip install -r requirements.txt
