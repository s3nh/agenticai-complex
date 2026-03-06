import json
import logging
from typing import Any

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from config import config
from tools.document_loader import DocumentLoader
from tools.vllm_client import VLLMClient

logger = logging.getLogger(__name__)

loader = DocumentLoader(tesseract_cmd=config.TESSERACT_CMD)
vllm_client = VLLMClient(
    base_url=config.VLLM_BASE_URL,
    api_key=config.VLLM_API_KEY,
    model=config.VLLM_MODEL,
)

EXTRACTION_PROMPT = """
You are a document data extraction expert.
Given the following document text (and optionally an image), extract all key fields.

Return a JSON object with:
- "key_fields": dict of extracted field names to values (e.g. invoice_number, date, amount, vendor, etc.)
- "confidence": float 0.0-1.0 for overall extraction confidence
- "notes": any relevant observations

Document text:
{text}

Return ONLY valid JSON.
"""


def extract_document_data(file_path: str) -> dict:
    """
    Loads a document from disk and extracts structured data from it.
    Handles PDFs (native text or scanned), images.

    Args:
        file_path: Absolute or relative path to the document file.

    Returns:
        A dict with raw_text, key_fields, confidence, source_file.
    """
    try:
        doc = loader.load(file_path)
        text = doc["text"]
        images_b64 = doc.get("images_b64", [])

        if config.INFERENCE_MODE == "vllm":
            if images_b64 and doc.get("is_scanned"):
                # Use vision model for scanned docs
                raw = vllm_client.chat_with_image(
                    prompt=EXTRACTION_PROMPT.format(text=text[:2000]),
                    image_b64=images_b64[0],
                )
            else:
                raw = vllm_client.chat(
                    prompt=EXTRACTION_PROMPT.format(text=text[:4000])
                )
            # Parse JSON from vLLM response
            parsed = _safe_json_parse(raw)
        else:
            # Gemini handles this via ADK tool call, return text for agent to process
            parsed = {"raw_text_for_agent": text[:6000]}

        return {
            "raw_text": text,
            "key_fields": parsed.get("key_fields", {}),
            "confidence": parsed.get("confidence", 0.5),
            "source_file": file_path,
            "images_available": len(images_b64),
        }

    except Exception as e:
        logger.error(f"Extraction failed for {file_path}: {e}")
        return {"error": str(e), "source_file": file_path}


def _safe_json_parse(text: str) -> dict:
    """Extract JSON from model output that may have surrounding text."""
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
    except Exception:
        pass
    return {}


# ADK FunctionTool wrapper
extract_tool = FunctionTool(func=extract_document_data)

extraction_agent = LlmAgent(
    name="extraction_agent",
    model=config.GEMINI_MODEL,
    description=(
        "Extracts structured data from documents (PDFs, scanned images, invoices, contracts). "
        "Returns key fields, raw text, and confidence score."
    ),
    instruction=(
        "You are a document extraction specialist. "
        "Use the extract_document_data tool to load and extract information from the given file path. "
        "Return the extracted fields as a structured summary. "
        "If the document is scanned/image-based, note that OCR was used."
    ),
    tools=[extract_tool],
)
