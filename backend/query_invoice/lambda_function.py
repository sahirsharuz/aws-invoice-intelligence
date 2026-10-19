import json
import pg8000.native

DB_HOST = ""
DB_NAME = ""
DB_USER = ""
DB_PASSWORD = ""
DB_PORT =


def lambda_handler(event, context):
    try:
        conn = pg8000.native.Connection(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            database=DB_NAME,
            port=DB_PORT,
            timeout=60
        )

        print("FULL EVENT:", json.dumps(event))  # Log the full event for debugging 


        query_params = event.get("queryStringParameters") or {}

        print("QUERY PARAMS:", query_params)

        vendor = query_params.get("vendor")
        category = query_params.get("category")
        invoice_number = query_params.get("invoice_number")
        min_price = query_params.get("min_price") 

        print("VENDOR:", vendor)
        print("CATEGORY:", category)
        print("INVOICE_NUMBER:", invoice_number)
        print("MIN_PRICE:", min_price)

        
        sql = """
        SELECT
            invoice_number,
            vendor_name,
            purchase_price,
            category,
            created_at
        FROM invoices
        WHERE 1 = 1
        """

        params = {}

        if vendor:
            sql += " AND vendor_name LIKE :vendor"
            params["vendor"] = f"%{vendor}%"

        if category:
            sql += " AND category LIKE :category"
            params["category"] = f"%{category}%"

        if invoice_number:
            sql += " AND invoice_number = :invoice_number"
            params["invoice_number"] = invoice_number

        if min_price:
            sql += " AND purchase_price >= :min_price"
            params["min_price"] = float(min_price)

        sql += " ORDER BY created_at DESC LIMIT 50"

        results = conn.run(sql, **params)

        conn.close()

        invoices = []

        for row in results:
            invoices.append({
                "invoice_number": row[0],
                "vendor_name": row[1],
                "purchase_price": float(row[2]) if row[2] else None,
                "category": row[3],
                "created_at": str(row[4])
            })

        return {
            "statusCode": 200,
            "body": json.dumps({
                "count": len(invoices),
                "results": invoices
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": str(e)
        }
    

    ##test