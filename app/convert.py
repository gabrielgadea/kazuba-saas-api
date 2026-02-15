"""Document conversion endpoint."""

from fastapi import UploadFile, File, HTTPException
from typing import Optional


async def convert_document(
    file: UploadFile = File(...),
    output_format: str = "markdown"
) -> dict:
    """
    Convert uploaded document to structured format.
    
    For MVP: placeholder. Will integrate kazuba-converter.
    """
    # Validate file type
    allowed_types = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        "text/markdown",
    ]
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}"
        )
    
    # TODO: Integrate with kazuba-converter
    # For now, return placeholder
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "output_format": output_format,
        "status": "converted",
        "content": "# Placeholder\n\nActual conversion will be implemented.",
    }
