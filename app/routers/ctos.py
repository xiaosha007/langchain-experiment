from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from app.internal.extractors.ctos import CTOSExtractor

router = APIRouter(prefix="/ctos", tags=["ctos"])

@router.post("/upload")
async def upload_ctos_pdf(
    file: UploadFile = File(...),
):
    """
    Upload a CTOS company report PDF and extract data from it.
    
    Args:
        file: The CTOS PDF file to process
        
    Returns:
        JSON with extracted information from the CTOS report
    """
    # Check if the file is a PDF
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        # Read the file content
        content = await file.read()
        
        # Create an extractor - no prompt needed with rule-based approach
        extractor = CTOSExtractor()
        
        # Extract data from the PDF
        extraction_result = extractor.extract_from_pdf_bytes(content)
        
        return JSONResponse(
            status_code=200,
            content={"data": extraction_result}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}") 