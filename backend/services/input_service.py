from __future__ import annotations

import io
import re
from pathlib import Path

from fastapi import UploadFile
from PIL import Image
import pytesseract

# Code file extensions (decoded as UTF-8 text, with BOM strip).
_CODE_SUFFIXES = frozenset({".py", ".java", ".c"})

# Image extensions passed to OCR.
_IMAGE_SUFFIXES = frozenset({".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"})


def _suffix_from_upload(filename: str | None) -> str:
    """Return lowercase file suffix including dot, or empty string."""
    if not filename:
        return ""
    return Path(filename).suffix.lower()


def _decode_bytes(raw: bytes) -> str:
    """Decode file bytes to text; strip BOM and normalize newlines."""
    if not raw:
        return ""
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return raw.decode(encoding).replace("\r\n", "\n").replace("\r", "\n")
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace").replace("\r\n", "\n")


def _clean_ocr_text(text: str) -> str:
    """
    Strip OCR noise: whitespace runs, odd control chars, keep printable lines.
    """
    if not text:
        return ""
    lines = []
    for line in text.splitlines():
        cleaned = "".join(ch for ch in line if ch.isprintable() or ch in "\t")
        cleaned = cleaned.strip()
        if cleaned:
            lines.append(cleaned)
    out = "\n".join(lines)
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.strip()


OCR_FALLBACK_MESSAGE = (
    "Could not extract readable code from this image. "
    "Try a sharper screenshot, better contrast, or paste the code as text."
)


async def extract_text_from_image(data: bytes) -> str:
    """
    Run Tesseract OCR on image bytes and return cleaned text.

    Raises:
        RuntimeError: If OCR fails (missing binary, invalid image, etc.).
    """
    try:
        with Image.open(io.BytesIO(data)) as img:
            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")
            raw = pytesseract.image_to_string(img)
    except Exception as exc:
        raise RuntimeError("OCR could not read this image.") from exc
    cleaned = _clean_ocr_text(raw)
    if not cleaned:
        raise RuntimeError("No text detected in image.")
    return cleaned


async def process_input(file: UploadFile | None, text: str | None) -> str:
    """
    Resolve code from optional file upload and/or text field.

    Priority: when a file is provided, it is processed first (code file or image OCR);
    otherwise non-empty ``text`` is returned. At least one source must yield content.

    Args:
        file: Multipart file (code or image), optional.
        text: Plain text field, optional.

    Returns:
        Extracted source code or text.

    Raises:
        ValueError: No input, unsupported extension, empty decode, or OCR failure message.
    """
    has_file = file is not None and (file.filename or "").strip() != ""
    raw_text = (text or "").strip()

    if not has_file and not raw_text:
        raise ValueError("Provide either a non-empty `text` field or a `file` upload.")

    if has_file and file is not None:
        data = await file.read()
        if not data:
            raise ValueError("Uploaded file is empty.")

        suffix = _suffix_from_upload(file.filename)

        if suffix in _CODE_SUFFIXES:
            decoded = _decode_bytes(data).strip()
            if not decoded:
                raise ValueError("File decoded to empty content.")
            return decoded

        if suffix in _IMAGE_SUFFIXES or (file.content_type or "").startswith("image/"):
            try:
                return await extract_text_from_image(data)
            except RuntimeError:
                return OCR_FALLBACK_MESSAGE

        raise ValueError(
            f"Unsupported file type '{suffix or 'unknown'}'. "
            f"Use {_CODE_SUFFIXES | _IMAGE_SUFFIXES} or a common image type."
        )

    return raw_text
