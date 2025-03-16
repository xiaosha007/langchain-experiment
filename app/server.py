#!/usr/bin/env python
from fastapi import FastAPI, UploadFile, HTTPException, File
from fastapi.responses import JSONResponse
from langchain.chat_models import ChatOpenAI
import os
from tempfile import NamedTemporaryFile
from .process_pdf import process_pdf
import logging
from .prompt import loan_report_prompt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple api server using Langchain's Runnable interfaces",
)

api_key = ""

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo-0125",
    api_key=api_key
)


@app.post("/analyze-ctos-report")
async def analyze_ctos_report(file: UploadFile = File(...)):
    """
    Upload a CTOS report PDF and get an AI-generated loan application analysis.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
    try:
        # Save uploaded file temporarily
        with NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()
            
            try:
                # Process the PDF
                text_chunks = process_pdf(temp_file.name)
                
                # Combine chunks and generate report
                full_text = "\n".join(text_chunks)
                
                # Generate loan report using LLM
                chain = loan_report_prompt | llm
                result = chain.invoke({"report_content": full_text})
                
                return JSONResponse(content={
                    "status": "success",
                    "analysis": result.content,
                    "filename": file.filename
                })
                
            finally:
                # Clean up temporary file
                os.unlink(temp_file.name)
                
    except Exception as e:
        logger.error(f"Error processing file {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")





