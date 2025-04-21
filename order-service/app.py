from flask import Flask, jsonify, request, render_template
import jwt
from functools import wraps
from datetime import datetime, timedelta
import psycopg2
import psycopg2.extras
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permitir solicitudes desde el frontend
app.config['SECRET_KEY'] = "mi_clave_secreta"
app.config['DATABASE_URL'] = "postgresql://user:password@db:5432/mydb"

# Conexión a la base de datos
def get_db_connection():
    conn = psycopg2.connect(app.config['DATABASE_URL'])
    return conn

# Crear tabla orders si no existe
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_name VARCHAR(100) NOT NULL,
            item VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

init_db()

# Decorador JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"message": "Token requerido"}), 403
        try:
            token = token.split(" ")[1]
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except Exception:
            return jsonify({"message": "Token inválido"}), 403
        return f(*args, **kwargs)
    return decorated

# API Endpoints
@app.route('/api/v1/orders', methods=['GET'])
@token_required
def get_orders():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM orders ORDER BY created_at DESC')
    orders = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([dict(order) for order in orders])

@app.route('/api/v1/orders/<int:order_id>', methods=['GET'])
@token_required
def get_order(order_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM orders WHERE id = %s', (order_id,))
    order = cur.fetchone()
    cur.close()
    conn.close()
    if order:
        return jsonify(dict(order))
    return jsonify({"message": "Orden no encontrada"}), 404

@app.route('/api/v1/orders', methods=['POST'])
@token_required
def create_order():
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO orders (user_name, item) VALUES (%s, %s) RETURNING id',
        (data['user'], data['item'])
    )
    order_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Orden creada", "id": order_id}), 201

# Interfaz Web
@app.route('/orders')
def orders_view():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('SELECT * FROM orders ORDER BY created_at DESC')
        orders = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('orders/index.html', orders=orders)
    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        return "Error cargando las órdenes", 500
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
