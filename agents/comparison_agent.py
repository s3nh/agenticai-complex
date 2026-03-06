import json
import logging

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from config import config
from tools.system_data import SystemDataStore

logger = logging.getLogger(__name__)
store = SystemDataStore(data_path=config.SYSTEM_DATA_PATH)

COMPARISON_PROMPT_TEMPLATE = """
Compare the extracted document fields against the system record.

Extracted from document:
{extracted}

System record:
{system_record}

Identify:
1. Matching fields (same key and value)
2. Mismatching fields (same key, different value)
3. Fields in document but not in system
4. Fields in system but not in document

Return JSON:
{{
  "matches": ["field1", "field2"],
  "mismatches": [{{"field": "amount", "doc_value": "15000", "system_value": "14500"}}],
  "missing_in_doc": ["field_name"],
  "missing_in_system": ["field_name"],
  "overall_match_score": <0.0-1.0>,
  "summary": "brief description"
}}
Return ONLY valid JSON.
"""


def compare_with_system(
    extracted_fields_json: str,
    record_id: str = "",
    search_field: str = "",
    search_value: str = "",
) -> dict:
    """
    Compares extracted document fields against system records.

    Args:
        extracted_fields_json: JSON string of extracted key-value pairs from the document.
        record_id: Direct system record ID to compare against (e.g. 'INV-2024-001').
        search_field: Field name to search by if record_id unknown (e.g. 'vendor').
        search_value: Value for the search_field lookup.

    Returns:
        Dict with matches, mismatches, missing fields, and overall match score.
    """
    try:
        extracted = json.loads(extracted_fields_json) if isinstance(extracted_fields_json, str) else extracted_fields_json
    except Exception:
        extracted = {}

    # Find system record
    system_record = None
    if record_id:
        system_record = store.get_record(record_id)
    elif search_field and search_value:
        results = store.search_by_field(search_field, search_value)
        if results:
            system_record = results[0]

    if not system_record:
        # Auto-search: try to find by any extracted field
        for field in ["invoice_number", "contract_id", "id_number", "document_id"]:
            if field in extracted:
                records = store.search_by_field(field, extracted[field])
                if records:
                    system_record = records[0]
                    break

    if not system_record:
        return {
            "error": "No matching system record found",
            "extracted": extracted,
            "overall_match_score": 0.0,
        }

    # Simple field comparison
    matches, mismatches, missing_in_doc, missing_in_system = [], [], [], []
    all_keys = set(extracted.keys()) | set(system_record.keys())

    for key in all_keys:
        in_doc = key in extracted
        in_sys = key in system_record
        if in_doc and in_sys:
            if str(extracted[key]).lower().strip() == str(system_record[key]).lower().strip():
                matches.append(key)
            else:
                mismatches.append({
                    "field": key,
                    "doc_value": extracted[key],
                    "system_value": system_record[key],
                })
        elif in_doc and not in_sys:
            missing_in_system.append(key)
        elif in_sys and not in_doc:
            missing_in_doc.append(key)

    score = len(matches) / max(len(all_keys), 1)

    return {
        "matches": matches,
        "mismatches": mismatches,
        "missing_in_doc": missing_in_doc,
        "missing_in_system": missing_in_system,
        "overall_match_score": round(score, 3),
        "system_record_id": system_record.get("id", record_id),
    }


compare_tool = FunctionTool(func=compare_with_system)

comparison_agent = LlmAgent(
    name="comparison_agent",
    model=config.GEMINI_MODEL,
    description=(
        "Compares extracted document data against system records to find "
        "matches, mismatches, and missing fields."
    ),
    instruction=(
        "You are a data reconciliation specialist. "
        "Use compare_with_system with the extracted JSON fields and either a direct record_id "
        "or search parameters. Identify discrepancies and compute a match score. "
        "Report all mismatches clearly with doc vs. system values."
    ),
    tools=[compare_tool],
)
