from flask import Flask, request, jsonify
import sqlite3
import bcrypt

app = Flask(__name__)
DB = "tareas.db"


def init_db():
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario   TEXT    UNIQUE NOT NULL,
                contrasena  TEXT    NOT NULL
            )
        """)
        con.commit()


def get_user(usuario):
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute("SELECT usuario, contrasena FROM usuarios WHERE usuario = ?", (usuario,))
        return cur.fetchone()


def verificar_credenciales(usuario, contrasena):
    row = get_user(usuario)
    if row is None:
        return False
    _, hashed = row
    return bcrypt.checkpw(contrasena.encode(), hashed.encode())


@app.route("/registro", methods=["POST"])
def registro():
    data = request.get_json()
    if not data or "usuario" not in data or "contraseña" not in data:
        return jsonify({"error": "Faltan campos: usuario y contraseña"}), 400

    usuario    = data["usuario"].strip()
    contrasena = data["contraseña"]

    if not usuario or not contrasena:
        return jsonify({"error": "Usuario y contraseña no pueden estar vacíos"}), 400

    hashed = bcrypt.hashpw(contrasena.encode(), bcrypt.gensalt()).decode()

    try:
        with sqlite3.connect(DB) as con:
            con.execute("INSERT INTO usuarios (usuario, contrasena) VALUES (?, ?)", (usuario, hashed))
            con.commit()
        return jsonify({"mensaje": f"Usuario '{usuario}' registrado correctamente"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": f"El usuario '{usuario}' ya existe"}), 409


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or "usuario" not in data or "contraseña" not in data:
        return jsonify({"error": "Faltan campos: usuario y contraseña"}), 400

    usuario    = data["usuario"].strip()
    contrasena = data["contraseña"]

    if verificar_credenciales(usuario, contrasena):
        return jsonify({"mensaje": f"Bienvenido, {usuario}!"}), 200
    else:
        return jsonify({"error": "Usuario o contraseña incorrectos"}), 401


@app.route("/tareas", methods=["GET"])
def tareas():
    html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Bienvenido</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: #eef2f7;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,.1);
            padding: 48px 56px;
            text-align: center;
            max-width: 480px;
        }
        .icon { font-size: 3em; margin-bottom: 16px; }
        h1 { color: #2c3e50; font-size: 1.8em; margin-bottom: 10px; }
        p  { color: #777; font-size: 1em; line-height: 1.6; }
        .footer { margin-top: 32px; font-size: .8em; color: #bbb; }
    </style>
</head>
<body>
    <div class="card">
        <div class="icon">📋</div>
        <h1>¡Bienvenido al Sistema de Gestión de Tareas!</h1>
        <p>Has iniciado sesión correctamente. Aquí podrás gestionar tus tareas próximamente.</p>
        <p class="footer">Programacion sobre redes · PFO 2</p>
    </div>
</body>
</html>"""
    return html, 200, {"Content-Type": "text/html; charset=utf-8"}


if __name__ == "__main__":
    init_db()
    print("Servidor corriendo en http://127.0.0.1:5000")
    app.run(debug=True)