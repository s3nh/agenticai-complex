import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Google ADK / Gemini
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    # vLLM local server (OpenAI-compatible)
    VLLM_BASE_URL: str = os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1")
    VLLM_API_KEY: str = os.getenv("VLLM_API_KEY", "EMPTY")
    VLLM_MODEL: str = os.getenv("VLLM_MODEL", "Qwen/Qwen2.5-VL-7B-Instruct")

    # Mode: "gemini" | "vllm"
    INFERENCE_MODE: str = os.getenv("INFERENCE_MODE", "gemini")

    # OCR
    TESSERACT_CMD: str = os.getenv("TESSERACT_CMD", "tesseract")

    # System data source (mock path or DB URL)
    SYSTEM_DATA_PATH: str = os.getenv("SYSTEM_DATA_PATH", "data/system_records.json")

config = Config()
