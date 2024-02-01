from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error
from time import sleep
import os  # Import os module to access environment variables

# Database configuration (use environment variables)
db_config = {
    'host': os.getenv('DB_HOST', ''),  # Replace 'default_host' with your default or leave blank
    'database': os.getenv('DB_NAME', ''),  # Replace 'default_database' with your default or leave blank
    'user': os.getenv('DB_USER', ''),  # Replace 'default_user' with your default or leave blank
    'password': os.getenv('DB_PASSWORD', ''),  # Replace 'default_password' with your default or leave blank
    'port': os.getenv('DB_PORT', '3306')  # Default MySQL port; adjust if necessary
}

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({'message': 'Service is running'}), 200


@app.route('/charge_account', methods=['POST'])
def charge_account():
    data = request.json
    phone_number = data['phone_number']
    try:
        amount = float(data['amount'])
    except ValueError:
        return jsonify({'message': 'Invalid amount format'}), 400

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        cursor.execute(
            "INSERT INTO transactions (transaction_id, phone_number, amount, timestamp, status, customer_name) "
            "VALUES (UUID(), %s, %s, NOW(), 'completed', 'some_customer_name')",
            (phone_number, amount)
        )
        
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
    
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute(
            "SELECT SUM(amount) FROM transactions WHERE phone_number = %s GROUP BY phone_number",
            (phone_number,)
        )
        result = cursor.fetchone()
        total_amount = result[0] if result else 0
        return jsonify({'amount': total_amount}), 200
    except Error as e:
        print(f'Error: {e}')
        return jsonify({'message': 'Failed to check account'}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)
