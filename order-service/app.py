from flask import Flask, jsonify, request
import jwt
from functools import wraps
from datetime import datetime, timedelta

app = Flask(__name__)
SECRET_KEY = "mi_clave_secreta"  # En producción, usa Secrets Manager
users = [{"id": 1, "name": "Juan"}, {"id": 2, "name": "María"}]  # Simulación de BD

# Decorador para verificar el token JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"message": "Token requerido"}), 403
        try:
            token = token.split(" ")[1]  # Formato "Bearer <token>"
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except Exception:
            return jsonify({"message": "Token inválido"}), 403
        return f(*args, **kwargs)
    return decorated

# Login para obtener token
@app.route('/api/v1/login', methods=['POST'])
def login():
    data = request.get_json()
    if data.get('username') == 'admin' and data.get('password') == '12345':
        token = jwt.encode({
            'user': 'admin',
            'exp': datetime.utcnow() + timedelta(minutes=30)
        }, SECRET_KEY, algorithm="HS256")
        return jsonify({"token": token})
    return jsonify({"message": "Credenciales inválidas"}), 401

# GET: Obtener todos los usuarios
@app.route('/api/v1/users', methods=['GET'])
@token_required
def get_users():
    return jsonify(users)

# GET: Obtener un usuario por ID
@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    user = next((u for u in users if u["id"] == user_id), None)
    if user:
        return jsonify(user)
    return jsonify({"message": "Usuario no encontrado"}), 404

# POST: Crear un nuevo usuario
@app.route('/api/v1/users', methods=['POST'])
@token_required
def create_user():
    data = request.get_json()
    new_id = max(u["id"] for u in users) + 1 if users else 1
    new_user = {"id": new_id, "name": data["name"]}
    users.append(new_user)
    return jsonify({"message": "Usuario creado", "user": new_user}), 201

# PUT: Actualizar un usuario existente
@app.route('/api/v1/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    data = request.get_json()
    user = next((u for u in users if u["id"] == user_id), None)
    if user:
        user["name"] = data["name"]
        return jsonify({"message": "Usuario actualizado", "user": user})
    return jsonify({"message": "Usuario no encontrado"}), 404

# DELETE: Eliminar un usuario
@app.route('/api/v1/users/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(user_id):
    global users
    user = next((u for u in users if u["id"] == user_id), None)
    if user:
        users = [u for u in users if u["id"] != user_id]
        return jsonify({"message": "Usuario eliminado"})
    return jsonify({"message": "Usuario no encontrado"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
