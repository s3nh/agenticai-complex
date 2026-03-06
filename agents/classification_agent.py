import logging

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from config import config
from tools.vllm_client import VLLMClient

logger = logging.getLogger(__name__)

vllm_client = VLLMClient(
    base_url=config.VLLM_BASE_URL,
    api_key=config.VLLM_API_KEY,
    model=config.VLLM_MODEL,
)

CLASSIFICATION_PROMPT = """
Classify the following document text into one of these categories:
- invoice
- contract
- id_document
- receipt
- medical_report
- bank_statement
- other

Document text (first 2000 chars):
{text}

Return JSON: {{"category": "<category>", "confidence": <0.0-1.0>, "reasoning": "<brief reason>"}}
Return ONLY valid JSON.
"""


def classify_document(raw_text: str) -> dict:
    """
    Classifies a document into a predefined category based on its text content.

    Args:
        raw_text: The extracted text content of the document.

    Returns:
        Dict with 'category', 'confidence', and 'reasoning'.
    """
    try:
        if config.INFERENCE_MODE == "vllm":
            response = vllm_client.chat(
                prompt=CLASSIFICATION_PROMPT.format(text=raw_text[:2000]),
                system_prompt="You are a document classification expert. Return only JSON.",
            )
            from agents.extraction_agent import _safe_json_parse
            result = _safe_json_parse(response)
            if not result:
                result = {"category": "other", "confidence": 0.3, "reasoning": "Parse failed"}
            return result
        else:
            # Return text for Gemini ADK agent to classify inline
            return {"raw_text_snippet": raw_text[:2000], "mode": "gemini_inline"}

    except Exception as e:
        logger.error(f"Classification failed: {e}")
        return {"category": "other", "confidence": 0.0, "error": str(e)}


classify_tool = FunctionTool(func=classify_document)

classification_agent = LlmAgent(
    name="classification_agent",
    model=config.GEMINI_MODEL,
    description=(
        "Classifies documents into categories: invoice, contract, id_document, "
        "receipt, medical_report, bank_statement, or other."
    ),
    instruction=(
        "You are a document classification specialist. "
        "Use classify_document tool with the raw text of the document. "
        "Identify the most likely category and explain your reasoning. "
        "Valid categories: invoice, contract, id_document, receipt, medical_report, bank_statement, other."
    ),
    tools=[classify_tool],
)
