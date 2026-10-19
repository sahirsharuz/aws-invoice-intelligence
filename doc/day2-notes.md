# Day 2 Notes

## Objective
Set up core AWS infrastructure to store and manage invoice data.

## What Was Accomplished

### 1. S3 Storage Setup
- Created S3 bucket for invoice storage
- Configured folder structure:
  - uploads/
  - processed/
  - failed/

### 2. Aurora PostgreSQL Database
- Created Aurora PostgreSQL cluster
- Database name: invoice_app
- Connected using psql
- Configured security group for access

### 3. Database Schema
- Created invoices table
- Created invoice_line_items table
- Enabled UUID generation (pgcrypto)

### 4. Validation
- Inserted test invoice record
- Queried data successfully
- Verified DB connectivity

## Key Learnings
- Security group configuration is critical for DB access
- Structuring schema early avoids future complexity
- Organized S3 structure helps pipeline design

## Architecture Progress

S3 (created) → Aurora PostgreSQL (created)
Frontend (pending)
API (pending)
Textract (next)

## Next Steps (Day 3)
- Create Lambda function
- Integrate Textract
- Extract invoice fields
- Prepare DB insert logic

## Notes
- Aurora = source of truth
- S3 = raw storage only
- Chatbot will query database (not files)
