# agents/signature_agent.py
import logging
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from config import config
from tools.document_loader import DocumentLoader

logger = logging.getLogger(__name__)
loader = DocumentLoader(tesseract_cmd=config.TESSERACT_CMD)

def check_signature(file_path: str) -> dict:
    """
    Checks whether a document contains a signature.

    Args:
        file_path: Path to the document to inspect.

    Returns:
        Dict with 'signed' (bool), 'confidence' (float), 'method' (str), 'notes' (str).
    """
    try:
        doc = loader.load(file_path)
        text = doc.get("text", "").lower()
        images_b64 = doc.get("images_b64", [])

        # Heuristic: look for signature-related keywords
        sig_keywords = [
            "signature", "signed", "sign here", "authorized by",
            "signatory", "e-signature", "digitally signed", "/s/",
        ]
        keyword_hits = [kw for kw in sig_keywords if kw in text]
        has_image_sig = len(images_b64) > 0 and doc.get("is_scanned", False)

        if keyword_hits or has_image_sig:
            confidence = min(0.5 + 0.1 * len(keyword_hits) + (0.2 if has_image_sig else 0), 0.95)
            return {
                "signed": True,
                "confidence": round(confidence, 2),
                "method": "keyword_and_image" if has_image_sig else "keyword",
                "notes": f"Found keywords: {keyword_hits}",
            }
        else:
            return {
                "signed": False,
                "confidence": 0.7,
                "method": "keyword_scan",
                "notes": "No signature indicators found in text or image.",
            }
    except Exception as e:
        logger.error(f"Signature check failed: {e}")
        return {"signed": False, "confidence": 0.0, "error": str(e)}


signature_tool = FunctionTool(func=check_signature)

signature_agent = LlmAgent(
    name="signature_agent",
    model=config.GEMINI_MODEL,
    description=(
        "Detects whether a document has been signed. "
        "Checks for signature keywords, digital signature markers, and image-based signatures."
    ),
    instruction=(
        "You are a document signature detection specialist. "
        "Use the check_signature tool with the document file path. "
        "Report clearly: signed / unsigned / unclear, with your confidence level and reasoning."
    ),
    tools=[signature_tool],
)
