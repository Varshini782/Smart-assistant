from __future__ import annotations

from pydantic import BaseModel


class ProcessInputResponse(BaseModel):
    """Result of merging text and/or uploaded file into a single code string."""

    extracted_code: str
