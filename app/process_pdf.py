from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List
import logging

def process_pdf(pdf_path: str) -> List[str]:
    """
    Process a PDF file and prepare it for LLM ingestion.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        List[str]: List of text chunks suitable for LLM processing
        
    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        Exception: For other PDF processing errors
    """
    try:
        # Initialize PDF reader
        reader = PdfReader(pdf_path)
        
        # Extract text from all pages
        text = ""
        for page in reader.pages:
            text += page.extract_text()
            
        # Create text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            is_separator_regex=False,
        )
        
        # Split text into chunks
        chunks = text_splitter.split_text(text)
        
        logging.info(f"Successfully processed PDF: {pdf_path}")
        logging.info(f"Generated {len(chunks)} text chunks")
        
        return chunks
        
    except FileNotFoundError:
        logging.error(f"PDF file not found: {pdf_path}")
        raise
    except Exception as e:
        logging.error(f"Error processing PDF {pdf_path}: {str(e)}")
        raise
