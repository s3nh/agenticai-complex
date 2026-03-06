from pydantic import BaseModel, Field
from typing import Optional, List, Any
from enum import Enum


class DocumentType(str, Enum):
    INVOICE = "invoice"
    CONTRACT = "contract"
    ID_DOCUMENT = "id_document"
    RECEIPT = "receipt"
    MEDICAL_REPORT = "medical_report"
    BANK_STATEMENT = "bank_statement"
    OTHER = "other"


class SignatureStatus(str, Enum):
    SIGNED = "signed"
    UNSIGNED = "unsigned"
    UNCLEAR = "unclear"


class ExtractedDocumentData(BaseModel):
    raw_text: str = Field(default="", description="Full extracted text")
    document_type: Optional[DocumentType] = None
    signature_status: Optional[SignatureStatus] = None
    key_fields: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    source_file: str = ""


class ComparisonResult(BaseModel):
    matches: List[str] = Field(default_factory=list)
    mismatches: List[dict] = Field(default_factory=list)
    missing_in_doc: List[str] = Field(default_factory=list)
    missing_in_system: List[str] = Field(default_factory=list)
    overall_match_score: float = Field(default=0.0, ge=0.0, le=1.0)


class AgentResult(BaseModel):
    success: bool
    extracted: Optional[ExtractedDocumentData] = None
    comparison: Optional[ComparisonResult] = None
    error: Optional[str] = None
    agent_log: List[str] = Field(default_factory=list)
