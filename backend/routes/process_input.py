from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from backend.schemas.process_input import ProcessInputResponse
from backend.services.input_service import process_input

router = APIRouter(tags=["process-input"])


@router.post("/process-input", response_model=ProcessInputResponse)
async def post_process_input(
    text: str | None = Form(None),
    file: UploadFile | None = File(None),
) -> ProcessInputResponse:
    """
    Accept optional form fields ``text`` and ``file`` (code: .py, .java, .c or an image for OCR).

    When both are sent, the file takes precedence. At least one must provide usable content.
    """
    try:
        extracted = await process_input(file=file, text=text)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return ProcessInputResponse(extracted_code=extracted)
