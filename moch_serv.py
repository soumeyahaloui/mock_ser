from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error
from time import sleep

app = Flask(__name__)

# Database configuration (use your actual credentials)
db_config = {
    'host': 'sql11.freesqldatabase.com',
    'database': 'sql11681109',
    'user': 'sql11681109',
    'password': 'C1ex6u3Uaa',
    'port': '3306'
}

@app.route('/charge_account', methods=['POST'])
def charge_account():
    data = request.json
    phone_number = data['phone_number']
    try:
        amount = float(data['amount'])  # Convert string to float
    except ValueError:
        return jsonify({'message': 'Invalid amount format'}), 400

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        # Record the transaction
        cursor.execute(
            "INSERT INTO transactions (transaction_id, phone_number, amount, timestamp, status, customer_name) "
            "VALUES (UUID(), %s, %s, NOW(), 'completed', 'some_customer_name')",
            (phone_number, amount)
        )
        
        # Update the balance in the account_balances table
        cursor.execute(
            "INSERT INTO account_balances (phone_number, balance, last_updated) "
            "VALUES (%s, %s, NOW()) "
            "ON DUPLICATE KEY UPDATE balance = balance + VALUES(balance), last_updated = NOW()",
            (phone_number, amount)
        )
        
        connection.commit()
    except Error as e:
        return jsonify({'message': 'Failed to charge account', 'error': str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    return jsonify({'message': 'Account charged successfully'}), 200

    
@app.route('/check_account', methods=['POST'])
def check_account():
    data = request.json
    phone_number = data['phone_number']
    # Query the database for the amount
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute(
            "SELECT SUM(amount) FROM transactions WHERE phone_number = %s GROUP BY phone_number",
            (phone_number,)
        )
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        connection.close()
        total_amount = result[0] if result else 0
        return jsonify({'amount': total_amount}), 200
    except Error as e:
        print(f'Error: {e}')
        return jsonify({'message': 'Failed to check account'}), 500

if __name__ == '__main__':
    app.run(debug=True)