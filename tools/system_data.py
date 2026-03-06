import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# In production: replace with DB/API calls
MOCK_RECORDS = {
    "INV-2024-001": {
        "vendor": "ACME Corp",
        "amount": 15000.00,
        "currency": "USD",
        "date": "2024-11-01",
        "status": "pending",
    },
    "CONTRACT-2024-055": {
        "party_a": "TechCo Ltd",
        "party_b": "Client GmbH",
        "value": 250000.00,
        "start_date": "2025-01-01",
        "end_date": "2026-01-01",
        "signed": True,
    },
    "ID-DOC-2024-789": {
        "name": "John Doe",
        "id_number": "A1234567",
        "dob": "1985-06-15",
        "expiry": "2030-06-15",
    },
}


class SystemDataStore:
    def __init__(self, data_path: str = ""):
        self.records: dict[str, Any] = {}
        if data_path and Path(data_path).exists():
            with open(data_path) as f:
                self.records = json.load(f)
        else:
            self.records = MOCK_RECORDS
            logger.info("Using mock system data store")

    def get_record(self, record_id: str) -> dict | None:
        return self.records.get(record_id)

    def search_by_field(self, field: str, value: Any) -> list[dict]:
        results = []
        for rec_id, rec in self.records.items():
            if str(rec.get(field, "")).lower() == str(value).lower():
                results.append({"id": rec_id, **rec})
        return results

    def get_all(self) -> dict:
        return self.records
