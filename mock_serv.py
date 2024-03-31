
from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error
from time import sleep
import os  # Import os module to access environment variables
import logging


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


db_config = {
    'host': 'sql11.freesqldatabase.com',
    'database': 'sql11695666',
    'user': 'sql11695666',
    'password': '5Gy4bRlFwc',
    'port': os.getenv('DB_PORT', '3306')
}



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
        
         # Check if the phone number exists in the users table
        cursor.execute("SELECT phone_number FROM users WHERE phone_number = %s", (phone_number,))
        user_exists = cursor.fetchone()
        if not user_exists:
            return jsonify({'message': 'Phone number does not exist in the users table'}), 404

        # Insert the transaction into the users table
        cursor.execute(
            "UPDATE users SET balance = balance + %s WHERE phone_number = %s",
            (amount, phone_number)
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
            "SELECT balance FROM users WHERE phone_number = %s",
            (phone_number,)
        )
        
        # Log the SQL query executed
        app.logger.info(f"SQL Query: SELECT balance FROM users WHERE phone_number = '{phone_number}'")
        
        result = cursor.fetchone()
        if result:
            balance = result[0]
            return jsonify({'balance': balance}), 200
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

@app.route('/update_balance', methods=['POST'])
def update_balance():
    data = request.json
    phone_number = data.get('phone_number')
    new_total_amount = data.get('new_total_amount')

    if not phone_number or not new_total_amount:
        return jsonify({'message': 'Phone number and new total amount are required'}), 400
    
    connection = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        # Log the SQL query executed for updating the balance
        app.logger.info(f"SQL Query: UPDATE users SET balance = {new_total_amount} WHERE phone_number = '{phone_number}'")
        
        cursor.execute(
            "UPDATE users SET balance = %s WHERE phone_number = %s",
            (new_total_amount, phone_number)
        )
        
        connection.commit()
        return jsonify({'message': 'Account balance updated successfully'}), 200
    except Error as e:
        return jsonify({'message': 'Failed to update account balance', 'error': str(e)}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


if __name__ == '__main__':
    app.run(debug=True)
