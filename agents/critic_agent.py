# agents/critic_agent.py
"""
Critic agent: reviews outputs from other agents and decides if they are
good enough to pass forward, or if re-delegation / retry is needed.
This is the self-reflection loop that makes the system truly agentic.
"""
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from config import config
from tools.memory_store import memory_read_all, memory_write

read_all_tool = FunctionTool(func=memory_read_all)
write_tool = FunctionTool(func=memory_write)

CRITIC_INSTRUCTION = """
You are a quality evaluation critic for a document analysis pipeline.

Your job:
1. Read all current agent outputs from shared memory using memory_read_all.
2. Evaluate each output against these quality criteria:
   - Extraction: Are key_fields non-empty? Is confidence > 0.4?
   - Classification: Is category not 'other' unless truly unclassifiable? Is confidence > 0.5?
   - Signature: Is the result definitive (not 'unclear') when confidence > 0.6?
   - Comparison: Is match_score meaningful? Are mismatches explained?
3. For each agent output, produce a verdict: PASS | RETRY | ESCALATE
4. Write your evaluation to memory with key="critic_evaluation".

Output format (write to memory):
{
  "verdicts": {
    "extraction_agent": {"verdict": "PASS|RETRY|ESCALATE", "reason": "..."},
    "classification_agent": {"verdict": "PASS|RETRY|ESCALATE", "reason": "..."},
    ...
  },
  "overall": "PASS|PARTIAL|FAIL",
  "retry_agents": ["agent_name_if_retry_needed"],
  "escalation_notes": "any critical concerns"
}

Be strict but fair. Low confidence is not always a failure — note it but pass if effort was genuine.
"""

critic_agent = LlmAgent(
    name="critic_agent",
    model=config.GEMINI_MODEL,
    description=(
        "Quality evaluation critic. Reviews outputs from all sub-agents and determines "
        "whether each result is good enough or needs retry/escalation."
    ),
    instruction=CRITIC_INSTRUCTION,
    tools=[read_all_tool, write_tool],
)
