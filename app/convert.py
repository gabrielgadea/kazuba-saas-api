"""Document conversion module - Kazuba Converter Integration."""

import io
from fastapi import UploadFile, File, HTTPException
from typing import Optional


# Try to import optional dependencies
try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt",
    "text/markdown": "md",
}


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF using pypdf."""
    if not PYPDF_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="PDF processing not available. Install pypdf: pip install pypdf"
        )
    
    try:
        pdf_file = io.BytesIO(file_bytes)
        reader = pypdf.PdfReader(pdf_file)
        text_parts = []
        
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        
        return "\n\n".join(text_parts)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to extract text from PDF: {str(e)}"
        )


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from DOCX using python-docx."""
    if not DOCX_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="DOCX processing not available. Install python-docx: pip install python-docx"
        )
    
    try:
        docx_file = io.BytesIO(file_bytes)
        doc = Document(docx_file)
        text_parts = []
        
        for para in doc.paragraphs:
            if para.text.strip():
                text_parts.append(para.text)
        
        return "\n\n".join(text_parts)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to extract text from DOCX: {str(e)}"
        )


def extract_text_from_txt(file_bytes: bytes) -> str:
    """Extract text from plain text file."""
    try:
        # Try UTF-8 first
        return file_bytes.decode('utf-8')
    except UnicodeDecodeError:
        try:
            # Fallback to latin-1
            return file_bytes.decode('latin-1')
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to decode text file: {str(e)}"
            )


def convert_to_markdown(text: str, filename: str) -> str:
    """Convert extracted text to markdown format."""
    # Add metadata header
    markdown = f"""# {filename}

---

{text}

---

*Converted by Kazuba Converter*
"""
    return markdown


async def convert_document(
    file: UploadFile = File(...),
    output_format: str = "markdown"
) -> dict:
    """
    Convert uploaded document to structured format.
    
    Supports:
    - PDF (.pdf) - requires pypdf
    - Word (.docx) - requires python-docx  
    - Text (.txt)
    - Markdown (.md)
    
    Args:
        file: Uploaded file
        output_format: Desired output format (default: markdown)
    
    Returns:
        dict with conversion results including extracted text
    """
    # Validate file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. "
                   f"Supported types: {', '.join(ALLOWED_TYPES.keys())}"
        )
    
    # Read file content
    try:
        file_bytes = await file.read()
        if len(file_bytes) == 0:
            raise HTTPException(
                status_code=400,
                detail="Empty file uploaded"
            )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to read file: {str(e)}"
        )
    
    # Extract text based on file type
    file_type = ALLOWED_TYPES[file.content_type]
    
    if file_type == "pdf":
        extracted_text = extract_text_from_pdf(file_bytes)
    elif file_type == "docx":
        extracted_text = extract_text_from_docx(file_bytes)
    elif file_type in ("txt", "md"):
        extracted_text = extract_text_from_txt(file_bytes)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}"
        )
    
    # Convert to requested format
    if output_format == "markdown":
        content = convert_to_markdown(extracted_text, file.filename)
    elif output_format == "text":
        content = extracted_text
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported output format: {output_format}. "
                   f"Supported: markdown, text"
        )
    
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "file_type": file_type,
        "output_format": output_format,
        "status": "converted",
        "content": content,
        "content_length": len(content),
        "extracted_text_length": len(extracted_text),
    }
