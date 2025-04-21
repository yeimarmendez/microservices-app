import psycopg2
from flask import Flask, jsonify, request, render_template, redirect, url_for
import jwt
from functools import wraps
from datetime import datetime, timedelta

app = Flask(__name__)
SECRET_KEY = "mi_clave_secreta"

# Conexión a PostgreSQL
def get_db_connection():
    conn = psycopg2.connect(
        host="db",
        database="mydb",
        user="user",
        password="password"
    )
    return conn

# Inicializar la base de datos
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

init_db()

# Decorador para verificar token JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"message": "Token requerido"}), 403
        try:
            token_parts = auth_header.split()
            if len(token_parts) != 2 or token_parts[0] != 'Bearer':
                return jsonify({"message": "Formato de token inválido"}), 403
            token = token_parts[1]
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token expirado"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"message": "Token inválido"}), 403
        except Exception as e:
            return jsonify({"message": f"Error al verificar token: {str(e)}"}), 403
        return f(*args, **kwargs)
    return decorated

# Endpoint de login
@app.route('/api/v1/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"message": "Se esperaba JSON"}), 400
    data = request.get_json()
    if data.get('username') == 'admin' and data.get('password') == '12345':
        token = jwt.encode({
            'user': 'admin',
            'exp': datetime.utcnow() + timedelta(minutes=30)
        }, SECRET_KEY, algorithm="HS256")
        return jsonify({"token": token if isinstance(token, str) else token.decode('utf-8')}), 200
    return jsonify({"message": "Credenciales inválidas"}), 401

# API REST

@app.route('/api/v1/users', methods=['GET'])
@token_required
def get_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, name FROM users')
    users = [{"id": row[0], "name": row[1]} for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(users), 200

@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, name FROM users WHERE id = %s', (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return jsonify({"id": row[0], "name": row[1]}), 200
    return jsonify({"message": "Usuario no encontrado"}), 404

@app.route('/api/v1/users', methods=['POST'])
@token_required
def create_user():
    if not request.is_json:
        return jsonify({"message": "Se esperaba JSON"}), 400
    data = request.get_json()
    if 'name' not in data:
        return jsonify({"message": "Nombre requerido"}), 400
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO users (name) VALUES (%s) RETURNING id', (data['name'],))
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Usuario creado", "user": {"id": new_id, "name": data['name']}}), 201

@app.route('/api/v1/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    if not request.is_json:
        return jsonify({"message": "Se esperaba JSON"}), 400
    data = request.get_json()
    if 'name' not in data:
        return jsonify({"message": "Nombre requerido"}), 400
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE users SET name = %s WHERE id = %s', (data['name'], user_id))
    updated = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    if updated:
        return jsonify({"message": "Usuario actualizado", "user": {"id": user_id, "name": data['name']}}), 200
    return jsonify({"message": "Usuario no encontrado"}), 404

@app.route('/api/v1/users/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM users WHERE id = %s', (user_id,))
    deleted = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    if deleted:
        return jsonify({"message": "Usuario eliminado"}), 200
    return jsonify({"message": "Usuario no encontrado"}), 404

# Interfaz HTML mínima (opcional)
@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, name FROM users')
    users = [{"id": row[0], "name": row[1]} for row in cur.fetchall()]
    cur.close()
    conn.close()
    return render_template('index.html', users=users)

@app.route('/new', methods=['GET', 'POST'])
def new_user():
    if request.method == 'POST':
        name = request.form['name']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO users (name) VALUES (%s)', (name,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index'))
    return render_template('new_user.html')

@app.route('/edit/<int:user_id>', methods=['GET'])
def edit_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, name FROM users WHERE id = %s', (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if user:
        return render_template('edit_user.html', user={"id": user[0], "name": user[1]})
    return redirect(url_for('index'))

@app.route('/update/<int:user_id>', methods=['POST'])
def update_user_ui(user_id):
    name = request.form['name']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE users SET name = %s WHERE id = %s', (name, user_id))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:user_id>', methods=['POST'])
def delete_user_ui(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM users WHERE id = %s', (user_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Añade debug=True para desarrollo

