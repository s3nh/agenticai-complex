from google.adk.agents import LlmAgent

from config import config
from agents.extraction_agent import extraction_agent
from agents.classification_agent import classification_agent
from agents.signature_agent import signature_agent
from agents.comparison_agent import comparison_agent

ORCHESTRATOR_INSTRUCTION = """
You are the Document Intelligence Orchestrator. Your job is to coordinate a full document analysis pipeline.

When given a document file path:

1. **EXTRACTION** → Delegate to extraction_agent to extract all text and structured fields.
2. **CLASSIFICATION** → Delegate to classification_agent to identify the document type 
   (invoice, contract, id_document, receipt, medical_report, bank_statement, other).
3. **SIGNATURE CHECK** → Delegate to signature_agent to determine if the document is signed.
4. **COMPARISON** → Delegate to comparison_agent to compare extracted fields against system records.

After all sub-agents complete, synthesize a final report including:
- Document type and confidence
- Key extracted fields (formatted clearly)
- Signature status (signed / unsigned / unclear)
- System data comparison results (match score, mismatches)
- Any anomalies or concerns

Be concise and structured. Use bullet points and sections.
"""

orchestrator_agent = LlmAgent(
    name="document_orchestrator",
    model=config.GEMINI_MODEL,
    description=(
        "Master orchestrator for document analysis. Coordinates extraction, "
        "classification, signature checking, and system data comparison."
    ),
    instruction=ORCHESTRATOR_INSTRUCTION,
    sub_agents=[
        extraction_agent,
        classification_agent,
        signature_agent,
        comparison_agent,
    ],
)
