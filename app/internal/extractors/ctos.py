import io
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

from pypdf import PdfReader

class CTOSExtractor:
    def __init__(self):
        """
        Initialize the CTOS extractor.
        """
        pass
    
    def extract(self, text: str) -> Dict[str, Any]:
        """
        Extract structured data from CTOS text content using regex and pattern matching.
        
        Args:
            text: The text content from the CTOS PDF
            
        Returns:
            Dict containing structured data extracted from the report
        """
        result = {
            "company_name": None,
            "registration_number": None,
            "registration_date": None,
            "business_address": None,
            "nature_of_business": None,
            "credit_score": None,
            "financial_summaries": [],
            "directors": [],
            "legal_actions": []
        }
        
        # Extract company name (usually at the beginning of the report)
        company_name_match = re.search(r'(?:COMPANY PROFILE|COMPANY NAME)[:\s]+([^\n]+)', text, re.IGNORECASE)
        if company_name_match:
            result["company_name"] = company_name_match.group(1).strip()
        
        # Extract registration number
        reg_num_match = re.search(r'(?:REGISTRATION NO|REG\. NO|COMPANY NO)[.:\s]+([A-Z0-9-]+)', text, re.IGNORECASE)
        if reg_num_match:
            result["registration_number"] = reg_num_match.group(1).strip()
        
        # Extract registration date
        reg_date_match = re.search(r'(?:DATE OF REGISTRATION|REGISTRATION DATE)[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}\s+[A-Za-z]+\s+\d{2,4})', text, re.IGNORECASE)
        if reg_date_match:
            date_str = reg_date_match.group(1).strip()
            # Try to convert to a standard format
            try:
                # Handle different date formats
                date_formats = [
                    "%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y",
                    "%d %B %Y", "%d %b %Y", "%B %d, %Y", "%b %d, %Y"
                ]
                for date_format in date_formats:
                    try:
                        parsed_date = datetime.strptime(date_str, date_format)
                        result["registration_date"] = parsed_date.strftime("%Y-%m-%d")
                        break
                    except ValueError:
                        continue
            except Exception:
                # If parsing fails, just store the original string
                result["registration_date"] = date_str
        
        # Extract business address
        address_match = re.search(r'(?:BUSINESS ADDRESS|REGISTERED ADDRESS|ADDRESS)[:\s]+([^\n]+(?:\n[^\n]+){0,5})', text, re.IGNORECASE)
        if address_match:
            # Clean up any overly long matches or irrelevant content
            address = address_match.group(1).strip()
            # Truncate at common terminators 
            terminators = ["TEL:", "TELEPHONE:", "FAX:", "EMAIL:", "NATURE OF BUSINESS:"]
            for terminator in terminators:
                if terminator.lower() in address.lower():
                    address = address[:address.lower().find(terminator.lower())].strip()
            result["business_address"] = address
        
        # Extract nature of business
        business_match = re.search(r'(?:NATURE OF BUSINESS|PRINCIPAL ACTIVITIES)[:\s]+([^\n]+(?:\n[^\n]+){0,3})', text, re.IGNORECASE)
        if business_match:
            result["nature_of_business"] = business_match.group(1).strip()
        
        # Extract credit score
        credit_score_match = re.search(r'(?:CREDIT SCORE|CTOS SCORE)[:\s]+(\d+)', text, re.IGNORECASE)
        if credit_score_match:
            result["credit_score"] = credit_score_match.group(1).strip()
        
        # Extract financial summaries
        financial_section = self._extract_section(text, r'(?:FINANCIAL SUMMARY|FINANCIAL INFORMATION)', r'(?:SHAREHOLDERS|DIRECTORS|LEGAL ACTIONS)')
        if financial_section:
            # Extract financial tables 
            financial_data = self._extract_financial_data(financial_section)
            if financial_data:
                result["financial_summaries"] = financial_data
        
        # Extract directors information
        directors_section = self._extract_section(text, r'(?:DIRECTORS|BOARD OF DIRECTORS)', r'(?:SHAREHOLDERS|LEGAL ACTIONS|SUMMARY)')
        if directors_section:
            directors = self._extract_directors(directors_section)
            if directors:
                result["directors"] = directors
        
        # Extract legal actions
        legal_section = self._extract_section(text, r'(?:LEGAL ACTIONS|LEGAL SUITS|LITIGATION)', r'(?:CREDIT RATING|CREDIT SCORE|SUMMARY)')
        if legal_section:
            legal_actions = self._extract_legal_actions(legal_section)
            if legal_actions:
                result["legal_actions"] = legal_actions
        
        return result
    
    def _extract_section(self, text: str, start_pattern: str, end_pattern: str) -> Optional[str]:
        """Extract a section from the text between start and end patterns."""
        section_match = re.search(f"{start_pattern}(.*?)(?:{end_pattern}|$)", text, re.DOTALL | re.IGNORECASE)
        if section_match:
            return section_match.group(1).strip()
        return None
    
    def _extract_financial_data(self, financial_section: str) -> List[Dict[str, Any]]:
        """Extract financial data from the financial section."""
        financial_data = []
        
        # Look for year/date patterns
        year_matches = re.finditer(r'\b(?:FY|YEAR|Y/E)[:\s]*(\d{4})\b', financial_section, re.IGNORECASE)
        years = [match.group(1) for match in year_matches]
        
        # Look for common financial metrics
        metrics = [
            ("revenue", r'(?:REVENUE|TURNOVER|SALES)[:\s]*([\d,.]+)'),
            ("profit_before_tax", r'(?:PROFIT BEFORE TAX|PBT)[:\s]*([\d,.]+)'),
            ("profit_after_tax", r'(?:PROFIT AFTER TAX|PAT|NET PROFIT)[:\s]*([\d,.]+)'),
            ("total_assets", r'(?:TOTAL ASSETS)[:\s]*([\d,.]+)'),
            ("total_liabilities", r'(?:TOTAL LIABILITIES)[:\s]*([\d,.]+)'),
            ("shareholders_equity", r'(?:SHAREHOLDERS EQUITY|EQUITY)[:\s]*([\d,.]+)')
        ]
        
        # If we found years, try to extract data for each year
        if years:
            for year in years:
                year_data = {"year": year}
                for metric_name, metric_pattern in metrics:
                    # Try to find the metric in proximity to the year
                    year_proximity = 200  # Characters around the year to search
                    year_pos = financial_section.find(year)
                    if year_pos != -1:
                        year_context = financial_section[max(0, year_pos - year_proximity):min(len(financial_section), year_pos + year_proximity)]
                        metric_match = re.search(metric_pattern, year_context, re.IGNORECASE)
                        if metric_match:
                            value = metric_match.group(1).replace(',', '')
                            try:
                                # Try to convert to a numeric value
                                year_data[metric_name] = float(value)
                            except ValueError:
                                year_data[metric_name] = value
                
                if len(year_data) > 1:  # If we found at least one metric besides the year
                    financial_data.append(year_data)
        
        # If we couldn't find year-specific data, try general patterns
        if not financial_data:
            general_data = {}
            for metric_name, metric_pattern in metrics:
                metric_match = re.search(metric_pattern, financial_section, re.IGNORECASE)
                if metric_match:
                    value = metric_match.group(1).replace(',', '')
                    try:
                        general_data[metric_name] = float(value)
                    except ValueError:
                        general_data[metric_name] = value
            
            if general_data:
                financial_data.append(general_data)
        
        return financial_data
    
    def _extract_directors(self, directors_section: str) -> List[Dict[str, str]]:
        """Extract directors information from the directors section."""
        directors = []
        
        # Look for name and ID patterns (common in Malaysian company reports)
        director_matches = re.finditer(r'([A-Za-z\s]+)\s*(?:\(([A-Z0-9-]+)\))?', directors_section)
        for match in director_matches:
            name = match.group(1).strip()
            id_number = match.group(2).strip() if match.group(2) else None
            
            # Verify this is actually a name - must be at least 5 chars and not a header
            if len(name) >= 5 and not re.match(r'^(DIRECTOR|NAME|APPOINTMENT|ADDRESS)S?$', name, re.IGNORECASE):
                director = {"name": name}
                if id_number:
                    director["id_number"] = id_number
                
                # Try to find appointment date near the name
                appointment_match = re.search(fr'{re.escape(name)}.*?(?:APPOINTED|APPOINTMENT DATE)[:\s]+(\d{{1,2}}[/-]\d{{1,2}}[/-]\d{{2,4}}|\d{{1,2}}\s+[A-Za-z]+\s+\d{{2,4}})', 
                                             directors_section, re.IGNORECASE)
                if appointment_match:
                    director["appointment_date"] = appointment_match.group(1)
                
                directors.append(director)
        
        return directors
    
    def _extract_legal_actions(self, legal_section: str) -> List[Dict[str, str]]:
        """Extract legal actions information from the legal section."""
        legal_actions = []
        
        # Check if there are any legal actions
        if re.search(r'(?:NO LEGAL ACTIONS|NO LITIGATION|NO RECORD)', legal_section, re.IGNORECASE):
            return []
        
        # Try to find case references and details
        case_matches = re.finditer(r'(?:CASE|SUIT|REFERENCE)[:\s]+([A-Z0-9-/]+)', legal_section, re.IGNORECASE)
        for match in case_matches:
            case_ref = match.group(1).strip()
            case_data = {"reference": case_ref}
            
            # Try to find case details in proximity
            case_pos = legal_section.find(case_ref)
            if case_pos != -1:
                case_context = legal_section[case_pos:min(len(legal_section), case_pos + 500)]
                
                # Extract plaintiff/defendant info
                plaintiff_match = re.search(r'(?:PLAINTIFF|CLAIMANT)[:\s]+([^\n]+)', case_context, re.IGNORECASE)
                if plaintiff_match:
                    case_data["plaintiff"] = plaintiff_match.group(1).strip()
                
                defendant_match = re.search(r'(?:DEFENDANT|RESPONDENT)[:\s]+([^\n]+)', case_context, re.IGNORECASE)
                if defendant_match:
                    case_data["defendant"] = defendant_match.group(1).strip()
                
                # Extract case status
                status_match = re.search(r'(?:STATUS|CASE STATUS)[:\s]+([^\n]+)', case_context, re.IGNORECASE)
                if status_match:
                    case_data["status"] = status_match.group(1).strip()
                
                # Extract amount/claim value
                amount_match = re.search(r'(?:AMOUNT|VALUE|CLAIM)[:\s]+(RM\s*[\d,.]+|MYR\s*[\d,.]+|USD\s*[\d,.]+)', case_context, re.IGNORECASE)
                if amount_match:
                    case_data["amount"] = amount_match.group(1).strip()
            
            legal_actions.append(case_data)
        
        return legal_actions
    
    def extract_from_pdf_bytes(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """
        Extract data from a PDF file provided as bytes.
        
        Args:
            pdf_bytes: The PDF file content as bytes
            
        Returns:
            Dict containing structured data extracted from the report
        """
        # Extract text from PDF bytes
        pdf_file = io.BytesIO(pdf_bytes)
        pdf_reader = PdfReader(pdf_file)
        
        # Extract text from all pages
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n\n"
        
        # Process the extracted text
        return self.extract(text)
