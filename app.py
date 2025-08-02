from flask import Flask, request, Response
from flask_cors import CORS
import json
import pyodbc

app = Flask(__name__)
CORS(app)  # ✅ Allow all origins

# SQL Server connection details
server = '146.190.81.199'
database = 'Nuport'
username = 'sa'
password = 'RYUK1XdnQ5wvamI'
connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

def get_db_connection():
    return pyodbc.connect(connection_string)

@app.route('/customer', methods=['GET'])
def get_customer_info():
    phone = request.args.get('phone')
    if not phone:
        return Response(json.dumps({"error": "Missing phone number"}, ensure_ascii=False, default=str), mimetype='application/json')

    query = '''
        SELECT 
            MAX(CustomerName) AS CustomerName,
            CustomerPhoneNumber,
            MAX(CustomerAddress) AS CustomerAddress,
            COUNT(DISTINCT Invoice) AS TotalOrder,
            MAX(CreationDate) AS LastOrderDate
        FROM dbo.GBMaster
        WHERE CustomerPhoneNumber = ?
        GROUP BY CustomerPhoneNumber
    '''

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, (phone,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return Response(json.dumps({"message": "Customer not found"}, ensure_ascii=False, default=str), mimetype='application/json')

        result = {
            "CustomerName": row.CustomerName,
            "CustomerPhoneNumber": row.CustomerPhoneNumber,
            "CustomerAddress": row.CustomerAddress,
            "TotalOrder": row.TotalOrder,
            "LastOrderDate": str(row.LastOrderDate)
        }
        return Response(json.dumps(result, ensure_ascii=False, default=str), mimetype='application/json')
    except Exception as e:
        return Response(json.dumps({"error": str(e)}, ensure_ascii=False, default=str), mimetype='application/json')


@app.route('/top-products', methods=['GET'])
def get_top_products():
    phone = request.args.get('phone')
    if not phone:
        return Response(json.dumps({"error": "Missing phone number"}, ensure_ascii=False, default=str), mimetype='application/json')

    query = '''
        SELECT ProductName, COUNT(*) AS OrderCount
        FROM dbo.GBMaster
        WHERE CustomerPhoneNumber = ?
        GROUP BY ProductName
        ORDER BY OrderCount DESC
    '''

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, (phone,))
        rows = cursor.fetchall()
        conn.close()

        products = [{"ProductName": row.ProductName, "OrderCount": row.OrderCount} for row in rows]
        return Response(json.dumps(products, ensure_ascii=False, default=str), mimetype='application/json')
    except Exception as e:
        return Response(json.dumps({"error": str(e)}, ensure_ascii=False, default=str), mimetype='application/json')

@app.route('/order-info', methods=['GET'])
def get_order_info():
    phone = request.args.get('phone')
    if not phone:
        return Response(json.dumps({"error": "Missing phone number"}, ensure_ascii=False, default=str), mimetype='application/json')

    query = '''
        SELECT DISTINCT Invoice AS OrderID, CreationDate AS OrderDate, ProductName, SUM(ProductQty) AS ProductQty
        FROM dbo.GBMaster
        WHERE CustomerPhoneNumber = ?
        GROUP BY Invoice, CreationDate, ProductName
        ORDER BY CreationDate DESC, Invoice
    '''

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, (phone,))
        rows = cursor.fetchall()
        conn.close()

        orders = []
        for row in rows:
            orders.append({
                "OrderID": row.OrderID,
                "OrderDate": str(row.OrderDate),
                "ProductName": row.ProductName,
                "ProductQty": row.ProductQty
            })

        return Response(json.dumps(orders, ensure_ascii=False, default=str), mimetype='application/json')
    except Exception as e:
        return Response(json.dumps({"error": str(e)}, ensure_ascii=False, default=str), mimetype='application/json')

if __name__ == '__main__':
    app.run(host='192.168.30.16', port=5000, debug=True)
