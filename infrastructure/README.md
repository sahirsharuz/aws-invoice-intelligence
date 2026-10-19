

## AWS System Architecture

Invoice AI uses AWS serverless services to extract, normalize,
store, and query invoice information.

![Invoice AI AWS Architecture](README.md/aws-architecture.png)

### Core Technologies

- **Amazon S3:** Invoice document storage
- **AWS Lambda:** Invoice processing and API queries
- **Amazon Textract:** AI-powered invoice data extraction
- **Amazon Aurora PostgreSQL:** Structured data storage
- **Amazon API Gateway:** HTTP API for querying invoices
- **Amazon CloudWatch:** Logging and monitoring

### Architecture Highlights

- Serverless invoice processing
- Automated document extraction
- PostgreSQL-backed invoice search
- Duplicate invoice detection
- Aurora Serverless v2 cost optimization
  