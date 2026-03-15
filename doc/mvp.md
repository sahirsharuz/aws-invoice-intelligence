# Invoice AI MVP

## Goal
Upload an invoice, extract key fields, store them in Aurora PostgreSQL, and retrieve them through an API.

## Source of Truth
Aurora PostgreSQL is the authoritative source for invoice answers.

## Phase 1 Scope
- Upload invoice PDF/image
- Store file in S3
- Extract fields with Textract
- Save fields in Aurora PostgreSQL
- Retrieve invoice fields through API

## Fields to Capture
- invoice_number
- vendor_name
- invoice_date
- subtotal
- tax_amount
- total_amount
- purchase_price
- account_number
- category
- s3_key

## Later Phases
- Chatbot UI
- Natural language to SQL
- RAG for policy / explanation documents
- Invoice categorization improvements
