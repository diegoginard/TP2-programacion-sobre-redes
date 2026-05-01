"""
cliente.py  –  Cliente de consola para la API de Gestión de Tareas
Uso:  python cliente.py
"""

import requests

BASE = "http://127.0.0.1:5000"


def menu():
    print("\n╔══════════════════════════════╗")
    print("║   Crear/logear usuario       ║")
    print("╚══════════════════════════════╝")
    print("1. Registrar usuario")
    print("2. Iniciar sesión (login)")
    print("0. Salir")
    return input("Opción: ").strip()


def pedir_campo(mensaje):
    """Pide un campo y no permite dejarlo vacío."""
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("⚠ Este campo no puede estar vacío. Intentá de nuevo.")


def registrar():
    usuario    = pedir_campo("Nombre de usuario: ")
    contrasena = pedir_campo("Contraseña: ")
    r = requests.post(f"{BASE}/registro", json={"usuario": usuario, "contraseña": contrasena})
    print(f"[{r.status_code}] {r.json()}")


def login():
    usuario    = pedir_campo("Usuario: ")
    contrasena = pedir_campo("Contraseña: ")
    r = requests.post(f"{BASE}/login", json={"usuario": usuario, "contraseña": contrasena})
    print(f"[{r.status_code}] {r.json()}")
    if r.status_code == 200:
        import urllib.parse
        url = f"{BASE}/tareas?usuario={urllib.parse.quote(usuario)}&contraseña={urllib.parse.quote(contrasena)}"
        print(f"✅ Abriendo tus tareas en el navegador...")
        import webbrowser
        webbrowser.open(url)
        return usuario, contrasena
    return None, None


def ver_tareas(usuario, contrasena):
    r = requests.get(f"{BASE}/tareas", params={"usuario": usuario, "contraseña": contrasena})
    if r.status_code == 200:
        print("\n--- HTML recibido (fragmento) ---")
        # Mostrar solo el body para no saturar la consola
        html = r.text
        start = html.find("<body>")
        end   = html.find("</body>")
        print(html[start:end+7] if start != -1 else html[:800])
    else:
        print(f"[{r.status_code}] {r.json()}")


def agregar_tarea(usuario, contrasena):
    titulo = pedir_campo("Título de la tarea: ")
    r = requests.post(
        f"{BASE}/tareas/nueva",
        json={"usuario": usuario, "contraseña": contrasena, "titulo": titulo}
    )
    print(f"[{r.status_code}] {r.json()}")


def main():
    usuario = contrasena = None
    while True:
        op = menu()
        if op == "1":
            registrar()
        elif op == "2":
            usuario, contrasena = login()
        elif op == "3":
            if not usuario:
                print("⚠ Primero iniciá sesión (opción 2).")
            else:
                ver_tareas(usuario, contrasena)
        elif op == "4":
            if not usuario:
                print("⚠ Primero iniciá sesión (opción 2).")
            else:
                agregar_tarea(usuario, contrasena)
        elif op == "0":
            print("¡Hasta luego!")
            break
        else:
            print("Opción inválida.")


if __name__ == "__main__":
    main()
