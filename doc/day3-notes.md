# Day 3 Notes

## Objective
Build an AI-powered invoice extraction pipeline using AWS Textract and Lambda.

## What Was Accomplished

### 1. Lambda Setup
- Created Lambda function (Python)
- Configured IAM role with:
  - S3 access
  - Textract access
  - CloudWatch logging

### 2. Textract Integration
- Used analyze_expense API (purpose-built for invoices)
- Passed S3 document input to Textract
- Successfully retrieved structured response

### 3. Data Extraction Logic
- Parsed Textract response structure:
  ExpenseDocuments → SummaryFields
- Built extract_fields() function to map:
  - VENDOR_NAME → vendor_name
  - INVOICE_RECEIPT_ID → invoice_number
  - TOTAL → total_amount

### 4. Debugging & Fixes
- Fixed 'response not defined' error (function parameter issue)
- Fixed incorrect API usage:
  - analyze_document ❌
  - analyze_expense ✅
- Verified correct Lambda handler configuration

### 5. Output Validation
- Printed raw Textract response in logs
- Extracted clean structured data
- Tested with real invoice files in S3

## Current Pipeline

S3 → Lambda → Textract → Structured JSON

## Example Output

{
  "vendor_name": "DEVORE DESIGN",
  "invoice_number": "386747",
  "total_amount": "$0.00"
}

## Key Learnings

- Textract understands document structure, not just OCR
- API response format:
  ExpenseDocuments → SummaryFields → Type / ValueDetection
- Importance of safe parsing using .get()
- Separation of concerns:
  - Extraction layer (Textract)
  - Transformation layer (Lambda)
- AI output is not ready for DB → requires normalization

## Architecture Progress

[ S3 ]
   ↓
[ Lambda ]
   ↓
[ Textract ]
   ↓
[ extract_fields() ]
   ↓
[ Structured JSON ]

## Next Step (Day 4)

- Build normalization layer (clean + type conversion)
- Connect Lambda to Aurora PostgreSQL
- Insert structured data into invoices table
- Persist invoice records for querying

## Notes

- Aurora will be the source of truth
- S3 stores raw documents only
- Chatbot will query structured DB, not raw files

