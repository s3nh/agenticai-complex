import asyncio
import logging
import sys
from pathlib import Path

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from agents.orchestrator_agent import orchestrator_agent
from config import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

APP_NAME = "doc-agent"


async def run_document_analysis(file_path: str) -> str:
    """Run the full document analysis pipeline on a given file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Document not found: {file_path}")

    session_service = InMemorySessionService()
    runner = Runner(
        agent=orchestrator_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id="user_001",
    )

    user_message = Content(
        role="user",
        parts=[Part(text=f"Please analyze this document: {file_path}")],
    )

    logger.info(f"Starting document analysis for: {file_path}")
    logger.info(f"Inference mode: {config.INFERENCE_MODE}")

    final_response = ""
    async for event in runner.run_async(
        user_id="user_001",
        session_id=session.id,
        new_message=user_message,
    ):
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    final_response += part.text

    return final_response


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <document_path>")
        print("Examples:")
        print("  python main.py invoice.pdf")
        print("  python main.py contract_scan.jpg")
        sys.exit(1)

    file_path = sys.argv[1]

    result = asyncio.run(run_document_analysis(file_path))

    print("\n" + "=" * 60)
    print("DOCUMENT ANALYSIS REPORT")
    print("=" * 60)
    print(result)
    print("=" * 60)


if __name__ == "__main__":
    main()
