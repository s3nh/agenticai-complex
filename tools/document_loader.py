import base64
import io
import logging
from pathlib import Path
from typing import Union

import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

logger = logging.getLogger(__name__)


class DocumentLoader:
    """Loads documents from various sources: PDF (native text or scanned), images."""

    def __init__(self, tesseract_cmd: str = "tesseract"):
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def load(self, file_path: Union[str, Path]) -> dict:
        """
        Returns:
            {
                "text": str,
                "images_b64": list[str],   # base64-encoded page images
                "pages": int,
                "source": str,
                "is_scanned": bool
            }
        """
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == ".pdf":
            return self._load_pdf(path)
        elif suffix in {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"}:
            return self._load_image(path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

    def _load_pdf(self, path: Path) -> dict:
        doc = fitz.open(str(path))
        full_text = ""
        images_b64 = []

        for page_num, page in enumerate(doc):
            # Try native text extraction first
            page_text = page.get_text("text").strip()
            full_text += f"\n--- Page {page_num + 1} ---\n{page_text}"

        is_scanned = len(full_text.strip()) < 100  # Heuristic: very little text = scanned

        if is_scanned:
            logger.info(f"PDF appears scanned, running OCR on {path.name}")
            pil_pages = convert_from_path(str(path), dpi=200)
            full_text = ""
            for i, pil_img in enumerate(pil_pages):
                ocr_text = pytesseract.image_to_string(pil_img)
                full_text += f"\n--- Page {i + 1} ---\n{ocr_text}"
                images_b64.append(self._pil_to_b64(pil_img))
        else:
            # Render pages as images for vision model usage
            for page in doc:
                pix = page.get_pixmap(dpi=150)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                images_b64.append(self._pil_to_b64(img))

        doc.close()
        return {
            "text": full_text.strip(),
            "images_b64": images_b64,
            "pages": len(images_b64),
            "source": str(path),
            "is_scanned": is_scanned,
        }

    def _load_image(self, path: Path) -> dict:
        img = Image.open(path).convert("RGB")
        ocr_text = pytesseract.image_to_string(img)
        return {
            "text": ocr_text.strip(),
            "images_b64": [self._pil_to_b64(img)],
            "pages": 1,
            "source": str(path),
            "is_scanned": True,
        }

    @staticmethod
    def _pil_to_b64(img: Image.Image) -> str:
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return base64.b64encode(buf.getvalue()).decode("utf-8")
