# agents/planner_agent.py
"""
Planner agent: before any tool is called, this agent reasons about the task
and produces an explicit execution plan that the orchestrator uses to guide itself.
This separates PLANNING from EXECUTION — a core agentic principle.
"""
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from config import config
from tools.memory_store import memory_write, memory_read_all

write_tool = FunctionTool(func=memory_write)
read_all_tool = FunctionTool(func=memory_read_all)

PLANNER_INSTRUCTION = """
You are a strategic planning agent. Your ONLY job is to produce an execution plan.

Given a task description (usually a file path to analyze), produce a JSON plan:
{
  "goal": "what we are trying to achieve",
  "steps": [
    {"agent": "extraction_agent", "reason": "...", "input_hint": "..."},
    {"agent": "classification_agent", "reason": "...", "input_hint": "..."},
    ...
  ],
  "success_criteria": "what a good final result looks like",
  "contingencies": {
    "if_extraction_fails": "...",
    "if_classification_uncertain": "..."
  }
}

Available agents: extraction_agent, classification_agent, signature_agent, comparison_agent, critic_agent.

Rules:
- Do NOT always use all agents. If the task is simple, use fewer.
- Order agents based on data dependencies (extraction before classification).
- Use critic_agent when confidence might be low.
- Write the plan to memory using memory_write with key="execution_plan".
"""

planner_agent = LlmAgent(
    name="planner_agent",
    model=config.GEMINI_MODEL,
    description=(
        "Strategic planning agent. Given a task, produces an explicit step-by-step "
        "execution plan stored in shared memory. Decides which agents to invoke and why."
    ),
    instruction=PLANNER_INSTRUCTION,
    tools=[write_tool, read_all_tool],
)
