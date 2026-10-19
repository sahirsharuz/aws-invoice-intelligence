# Day 4 — AWS Invoice AI Pipeline (Phase 2 Complete)

## Overview

Today was a major breakthrough in the invoice automation build.

After resolving multiple infrastructure and networking challenges across AWS Lambda, Aurora PostgreSQL, RDS Proxy, VPC security groups, and Textract endpoints, the pipeline is now successfully processing invoices end-to-end.

---

## Achievements

- Lambda securely connected to Aurora PostgreSQL
- AWS Textract AnalyzeExpense integrated successfully
- Raw Textract JSON responses persisted into PostgreSQL
- Invoice metadata extraction working:
  - Invoice Number
  - Vendor Name
  - Purchase Price
  - Categories
- Line item extraction logic implemented
- Dynamic fallback pricing logic added for invoices without TOTAL fields
- PostgreSQL relational schema finalized:
  - invoices
  - invoice_line_items
- Full VPC endpoint + private networking configuration completed

---

## Key Learning

One of the biggest learnings today:

AI document extraction is not just infrastructure — it’s semantic interpretation.

The invoice total was not stored as a traditional TOTAL field, so extraction logic had to intelligently identify pricing buried inside line item structures returned by Textract.

---

## Final Extracted Output

- Invoice #: 386747
- Vendor: DEVORE DESIGN
- Purchase Price: $847.00
- Category: Real Estate Services

---

## Tech Stack

- AWS Lambda
- AWS Textract
- Aurora PostgreSQL
- RDS Proxy
- VPC Endpoints
- Python
- pg8000
- Amazon S3

---

## Infrastructure Challenges Resolved

### Networking

- Configured Lambda inside VPC
- Established RDS Proxy connectivity
- Configured Aurora security group inbound/outbound rules
- Created Textract VPC endpoint
- Fixed endpoint security group communication
- Enabled private AWS service access without NAT Gateway

### Database

- Verified PostgreSQL connectivity from Lambda
- Added JSONB storage for raw Textract responses
- Implemented invoice and invoice line item relational schema
- Validated foreign key constraints and cleanup workflows

### AI Extraction

- Debugged Textract AnalyzeExpense response structures
- Inspected SummaryFields and LineItemGroups directly from PostgreSQL JSONB data
- Implemented fallback extraction logic for invoices lacking TOTAL fields
- Mapped PRICE fields from line items into normalized purchase_price values

---

## Current System Flow

\`\`\`text
S3 Upload
   ↓
AWS Lambda Trigger
   ↓
Textract AnalyzeExpense
   ↓
Field Extraction + Normalization
   ↓
Aurora PostgreSQL Storage
   ↓
Structured Invoice Analytics
\`\`\`

---

## Next Phase

### Day 5 Goals

- Build API layer for invoice querying
- Add chatbot query interface
- Enable natural language invoice lookups
- Create invoice analytics and reporting endpoints
- Implement invoice search by:
  - Vendor
  - Amount
  - Date
  - Category
- Begin Retrieval-Augmented Generation (RAG) experimentation for invoice Q&A

