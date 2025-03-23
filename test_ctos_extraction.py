import argparse
import json
import os
from app.internal.extractors.ctos import CTOSExtractor

def main():
    parser = argparse.ArgumentParser(description='Extract data from a CTOS PDF report.')
    parser.add_argument('--pdf', type=str, default='docs/CTOS-Company-Report-Sample.pdf',
                        help='Path to the CTOS PDF file')
    parser.add_argument('--output', type=str, default='ctos_output.json',
                        help='Output file path for the JSON result')
    
    args = parser.parse_args()
    
    # Check if the file exists
    if not os.path.exists(args.pdf):
        print(f"Error: File {args.pdf} does not exist")
        return
    
    print(f"Processing PDF: {args.pdf}")
    
    # Create the extractor - no prompt needed with rule-based approach
    extractor = CTOSExtractor()
    
    # Read the PDF file
    with open(args.pdf, 'rb') as f:
        pdf_bytes = f.read()
    
    # Extract data
    result = extractor.extract_from_pdf_bytes(pdf_bytes)
    
    # Write the result to a JSON file
    with open(args.output, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"Extraction complete! Results written to {args.output}")
    
    # Print some key information
    print("\nExtracted Information:")
    print("---------------------")
    for key, value in result.items():
        if isinstance(value, (str, int, float)) or value is None:
            print(f"{key}: {value}")
        elif isinstance(value, list) and len(value) > 0:
            print(f"{key}: [{len(value)} items]")
        elif isinstance(value, dict):
            print(f"{key}: {json.dumps(value, indent=2)}")
    

if __name__ == "__main__":
    main() 