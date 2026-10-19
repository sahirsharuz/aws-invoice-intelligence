import boto3
import pg8000.native
import json
import re
from datetime import datetime
from urllib.parse import unquote_plus

textract = boto3.client("textract")

DB_HOST = ""
DB_NAME = ""
DB_USER = ""
DB_PASSWORD = ""
DB_PORT = 


def lambda_handler(event, context):
    try:
        print("STEP 1: Lambda started")

        # Determine if the event is from S3 or a direct invocation

        if "Records" in event:
            print ("Invocation Source: S3 Event")
            record=event["Records"][0]
            bucket = record["s3"]["bucket"]["name"]
            key = unquote_plus(record["s3"]["object"]["key"])
        else:
            print("Invocation Source: Manual Invocation")
            bucket = event.get("bucket")
            key = event.get("key")

        print(f"STEP 2: Input received → bucket={bucket}, key={key}")

        print("STEP 3: Calling Textract...")
        textract_response = textract.analyze_expense(
            Document={
                "S3Object": {
                    "Bucket": bucket,
                    "Name": key
                }
            }
        )
        print("STEP 4: Textract completed")

        print("STEP 5: Extracting fields and line items...")
        raw_data = extract_fields(textract_response)
        print("RAW DATA:", raw_data)

        print("STEP 6: Normalizing data...")
        clean_data = normalize_data(raw_data, key)
        print("CLEAN DATA:", clean_data)



        print("STEP 7: Connecting to DB...")
        conn = pg8000.native.Connection(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            database=DB_NAME,
            port=DB_PORT,
            timeout=60
        )
        print("STEP 8: DB connection established")

        if invoice_exists(conn, clean_data.get("s3_key")):
            print("Invoice already exists in the database. Skipping insertion.")
            conn.close()
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "status": "duplicate",
                    "message": "Invoice already exists in the database.",
                    "data": clean_data.get("s3_key")
                })
            }

        print("STEP 9: Inserting invoice...")
        invoice_id = insert_invoice(conn, clean_data, textract_response)

        print("STEP 10: Inserting line items...")
        insert_line_items(conn, invoice_id, clean_data.get("line_items", []))

        conn.close()
        print("STEP 11: Insert complete")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "success",
                "invoice_id": str(invoice_id),
                "data": clean_data
            })
        }

    except Exception as e:
        print("ERROR OCCURRED:", str(e))
        return {
            "statusCode": 500,
            "body": str(e)
        }


def extract_fields(response):
    data = {
        "line_items": [],
        "confidence_values": []
    }

    for doc in response.get("ExpenseDocuments", []):

       
        # SUMMARY FIELDS
        
        for field in doc.get("SummaryFields", []):

            field_type = field.get("Type", {}).get("Text")
            label = field.get("LabelDetection", {}).get("Text")
            value = field.get("ValueDetection", {}).get("Text")
            confidence = field.get("ValueDetection", {}).get("Confidence")

            print(
                f"SUMMARY FIELD → type={field_type}, "
                f"label={label}, value={value}"
            )

            if confidence is not None:
                data["confidence_values"].append(confidence)

            label_upper = (label or "").upper()
            label_lower = (label or "").lower()

            if field_type == "VENDOR_NAME":
                if not data.get("vendor_name"):
                    data["vendor_name"] = value

            elif field_type == "INVOICE_RECEIPT_ID":
                data["invoice_number"] = value

            elif field_type == "INVOICE_RECEIPT_DATE":
                data["invoice_date"] = value

            elif field_type == "SUBTOTAL":
                data["subtotal"] = value

            elif field_type == "TAX":
                data["tax_amount"] = value

            elif field_type== "AMOUNT_PAID":
                if "DEPOSIT" in label_upper:
                    data["deposit_amount"] = value

            elif field_type == "TOTAL":
                if label_upper == "TOTAL":
                    data["total_amount"] = value

            elif field_type == "AMOUNT_DUE":
                data["balance_due"] = value

            # Deposit is sometimes classified as OTHER,
            # so use the printed label as a fallback.
            if "DEPOSIT" in label_upper:
                data["deposit_amount"] = value

            if "balance due" in label_upper:
                if not data.get("balance_due"):
                    data["balance_due"] = value

        # -----------------------------
        # LINE ITEMS
        # -----------------------------
        for group in doc.get("LineItemGroups", []):
            for item in group.get("LineItems", []):

                line_item = {
                    "description": None,
                    "quantity": None,
                    "unit_price": None,
                    "line_total": None
                }

                item_text = None
                expense_row = None

                for field in item.get("LineItemExpenseFields", []):

                    field_type = field.get("Type", {}).get("Text")
                    value = field.get("ValueDetection", {}).get("Text")
                    confidence = field.get("ValueDetection", {}).get("Confidence")

                    print(f"LINE FIELD → {field_type}: {value}")

                    if confidence is not None:
                        data["confidence_values"].append(confidence)

                    if field_type == "ITEM":
                        item_text = value

                    elif field_type == "EXPENSE_ROW":
                        expense_row = value

                    elif field_type == "QUANTITY":
                        line_item["quantity"] = clean_number(value)

                    elif field_type in ["UNIT_PRICE", "PRICE"]:
                        line_item["unit_price"] = clean_money(value)

                    elif field_type in ["AMOUNT", "TOTAL"]:
                        line_item["line_total"] = clean_money(value)

                # Prefer the richer full row description
                if expense_row:
                    line_item["description"] = expense_row
                elif item_text:
                    line_item["description"] = item_text

                if any(line_item.values()):
                    data["line_items"].append(line_item)
                    print("PARSED LINE ITEM:", line_item)

    return data


def normalize_data(raw_data, s3_key):
    line_items = raw_data.get("line_items", [])

    line_totals = [
        item.get("line_total")
        for item in line_items
        if item.get("line_total") is not None
    ]

    unit_prices = [
        item.get("unit_price")
        for item in line_items
        if item.get("unit_price") is not None
    ]

    total_amount = clean_money(raw_data.get("total_amount"))

    # prefer invoice total.
    #only fall bacl to line item totals if TOTAL wasn't found

    if total_amount is not None:
        purchase_price = total_amount
    elif line_totals:
        purchase_price = max(line_totals)
    elif unit_prices:
        purchase_price = max(unit_prices)
    else:
        purchase_price = None

    confidence_values = raw_data.get("confidence_values", [])
    extraction_confidence = None

    if confidence_values:
        extraction_confidence = round(sum(confidence_values) / len(confidence_values), 2)

    category = categorize_invoice(raw_data.get("vendor_name"), line_items)

    description = None

    if line_items:
        description = line_items[0].get("description")

    return {
        "invoice_number": raw_data.get("invoice_number"),
        "vendor_name": raw_data.get("vendor_name"),
        "invoice_date": clean_date(raw_data.get("invoice_date")),
        "subtotal": clean_money(raw_data.get("subtotal")),
        "tax_amount": clean_money(raw_data.get("tax_amount")),
        "total_amount": total_amount,
        "purchase_price": purchase_price,
        "deposit_amount": clean_money(raw_data.get("deposit_amount")),
        "balance_due": clean_money(raw_data.get("balance_due")),
        "description": description,
        "account_number": None,
        "category": category,
        "s3_key": s3_key,
        "extraction_confidence": extraction_confidence,
        "line_items": line_items
    }

# check if INVOICE ALREADT EXISTS in the database before inserting

def invoice_exists(conn, s3_key):
    result = conn.run(
        """
        SELECT invoice_id FROM invoices WHERE s3_key = :s3_key
        LIMIT 1;
        """,
        s3_key=s3_key
    )
    return len(result) > 0

def insert_invoice(conn, data, textract_response):
    result = conn.run(
        """
        INSERT INTO invoices (
            invoice_id,
            invoice_number,
            vendor_name,
            invoice_date,
            purchase_price,
            subtotal,
            tax_amount,
            total_amount,
            deposit_amount,
            balance_due,
            description,
            account_number,
            category,
            s3_key,
            extraction_confidence,
            raw_textract_json
        )
        VALUES (
            gen_random_uuid(),
            :invoice_number,
            :vendor_name,
            :invoice_date,
            :purchase_price,
            :subtotal,
            :tax_amount,
            :total_amount,
            :deposit_amount,
            :balance_due,
            :description,
            :account_number,
            :category,
            :s3_key,
            :extraction_confidence,
            CAST(:raw_textract_json AS jsonb)
        )
        RETURNING invoice_id;
        """,
        invoice_number=data.get("invoice_number"),
        vendor_name=data.get("vendor_name"),
        invoice_date=data.get("invoice_date"),
        purchase_price=data.get("purchase_price"),
        subtotal=data.get("subtotal"),
        tax_amount=data.get("tax_amount"),
        total_amount=data.get("total_amount"),
        deposit_amount=data.get("deposit_amount"),
        balance_due=data.get("balance_due"),
        description=data.get("description"),
        account_number=data.get("account_number"),
        category=data.get("category"),
        s3_key=data.get("s3_key"),
        extraction_confidence=data.get("extraction_confidence"),
        raw_textract_json=json.dumps(textract_response, default=str)
    )

    return result[0][0]

def insert_line_items(conn, invoice_id, line_items):
    for item in line_items:
        conn.run(
            """
            INSERT INTO invoice_line_items (
                invoice_id,
                description,
                quantity,
                unit_price,
                line_total
            )
            VALUES (
                :invoice_id,
                :description,
                :quantity,
                :unit_price,
                :line_total
            );
            """,
            invoice_id=str(invoice_id),
            description=item.get("description"),
            quantity=item.get("quantity"),
            unit_price=item.get("unit_price"),
            line_total=item.get("line_total")
        )

def categorize_invoice(vendor_name, line_items):
    text = (vendor_name or "").lower()

    for item in line_items:
        text += " " + str(item.get("description") or "").lower()

    if "real estate" in text:
        return "Real Estate Services"
    elif "software" in text or "subscription" in text:
        return "Software"
    elif "electric" in text or "utility" in text:
        return "Utilities"
    elif "office" in text or "supplies" in text:
        return "Office Supplies"
    else:
        return "Other"


def clean_money(val):
    if val is None:
        return None

    val = str(val)
    val = re.sub(r"[^0-9.\-]", "", val)

    if not val:
        return None

    try:
        return float(val)
    except ValueError:
        return None


def clean_number(val):
    if val is None:
        return None

    val = str(val)
    val = re.sub(r"[^0-9.\-]", "", val)

    if not val:
        return None

    try:
        return float(val)
    except ValueError:
        return None


def clean_date(val):
    if not val:
        return None

    val = str(val).strip()

    formats = [
        "%m/%d/%Y",
        "%m-%d-%Y",
        "%Y-%m-%d",
        "%B %d, %Y",
        "%b %d, %Y"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(val, fmt).date().isoformat()
        except ValueError:
            pass

    return None