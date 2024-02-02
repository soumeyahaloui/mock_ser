from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error
from time import sleep
import os  # Import os module to access environment variables
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


db_config = {
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'port': os.getenv('DB_PORT', '3306')
}

# Add these print statements to check the values
print(f"DB_HOST: {os.getenv('DB_HOST')}")
print(f"DB_USER: {os.getenv('DB_USER')}")
print(f"DB_PASSWORD: {os.getenv('DB_PASSWORD')}")
print(f"DB_NAME: {os.getenv('DB_NAME')}")
print(f"DB_PORT: {os.getenv('DB_PORT', '3306')}")


app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({'message': 'Service is running'}), 200


@app.route('/charge_account', methods=['POST'])
def charge_account():
    data = request.json
    phone_number = data['phone_number']
    connection = None

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
    phone_number = data.get('phone_number')
    if not phone_number:
        return jsonify({'message': 'Phone number is required'}), 400
    
    connection = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute(
            "SELECT SUM(amount) FROM transactions WHERE phone_number = %s GROUP BY phone_number",
            (phone_number,)
        )
        result = cursor.fetchone()
        if result:
            total_amount = result[0]
            return jsonify({'amount': total_amount}), 200
        else:
            return jsonify({'message': 'No data found for the given phone number'}), 404
    except Error as e:
        app.logger.error(f'Error connecting to MySQL Database: {e}')
        return jsonify({'message': 'Failed to check account', 'error': str(e)}), 500
    except Exception as e:
        app.logger.error(f'Unexpected error: {e}')
        return jsonify({'message': 'An unexpected error occurred', 'error': str(e)}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


if __name__ == '__main__':
    app.run(debug=True)
