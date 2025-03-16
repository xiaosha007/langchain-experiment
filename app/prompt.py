from langchain.prompts import ChatPromptTemplate

# Create loan report analysis prompt
loan_report_prompt = ChatPromptTemplate.from_template("""
You are a professional loan officer analyzing a CTOS report. Based on the following report content, 
generate a comprehensive loan application analysis. Focus on:

1. Credit history and payment behavior
2. Risk assessment
3. Debt service ratio analysis
4. Recommendation for loan approval/rejection
5. Suggested loan terms (if recommended for approval)

Report content:
{report_content}

Please provide a detailed, professional analysis structured in clear sections.
""")