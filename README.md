┌─────────────────────────────────────────────────────────┐
│                   Document Input                        │
│          (PDF native / PDF scanned / Image)             │
└──────────────────────┬──────────────────────────────────┘
                       │
              ┌────────▼────────┐
              │ DocumentLoader  │  PyMuPDF + Tesseract OCR
              │ + base64 images │  pdf2image
              └────────┬────────┘
                       │
        ┌──────────────▼──────────────────────┐
        │     Orchestrator Agent (ADK)        │
        │     google/gemini-2.0-flash         │
        └──┬──────┬──────────┬──────────┬─────┘
           │      │          │          │
    ┌──────▼──┐ ┌─▼───────┐ ┌▼────────┐ ┌▼──────────┐
    │Extract  │ │Classify │ │Sign.    │ │Compare    │
    │Agent    │ │Agent    │ │Agent    │ │Agent      │
    └──┬──────┘ └─┬───────┘ └┬────────┘ └┬──────────┘
       │          │          │           │
       └──────────┴──────────┴───────────┘
                       │
            ┌──────────▼──────────┐
            │  vLLM (optional)    │
            │  local model server │
            │  OpenAI-compatible  │
            └─────────────────────┘
