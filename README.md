# CTOS PDF Data Extraction API

This project provides an API for extracting structured data from CTOS company report PDFs using a rule-based pattern matching approach.

## Features

- Upload CTOS PDF reports via API
- Extract key information like company details, financials, and legal information using pattern matching
- Structured JSON output with all relevant data
- No need for AI/LLM services or API keys

## Setup

1. Install dependencies:

```bash
pip install -e .
```

## Running the API

Start the FastAPI server with:

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## API Endpoints

### Upload CTOS PDF

```
POST /ctos/upload
```

Parameters:

- `file`: The CTOS PDF file to process (multipart/form-data)

Response:

```json
{
  "data": {
    "company_name": "Example Company Sdn Bhd",
    "registration_number": "123456-A",
    "registration_date": "2010-01-01",
    "business_address": "123 Example Street...",
    "nature_of_business": "Manufacturing",
    "credit_score": "85",
    "financial_summaries": [...],
    "directors": [...],
    "legal_actions": [...]
  }
}
```

## Testing with Sample PDF

You can test the extraction with the included sample file:

```bash
python test_ctos_extraction.py
```

This will process the sample PDF and output the extracted data to `ctos_output.json`.

## Extraction Method

The system uses regular expressions and pattern matching to extract data from the PDF documents. The extraction is based on common CTOS report formats and recognizes patterns for:

- Company information (name, registration, address)
- Financial data
- Director information
- Legal actions

This approach doesn't require any external AI services and works offline.
