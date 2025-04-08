import socket
import threading
from datetime import datetime

BUFFER = 1024

def mostrar_tablero(tablero, tamaño):
    print("\nTABLERO ACTUAL")
    print("   ", end="")
    for i in range(tamaño):
        print(i, end=" ")
    print()
    for i in range(tamaño):
        print(f"{i} |", end="")
        for j in range(tamaño):
            print(tablero[i * tamaño + j], end="|")
        print()
    print()

def pedir_jugada(tamaño):
    try:
        fila = int(input(f"Ingrese fila (0 a {tamaño - 1}): "))
        columna = int(input(f"Ingrese columna (0 a {tamaño - 1}): "))
        if 0 <= fila < tamaño and 0 <= columna < tamaño:
            return f"{fila}{columna}"
        else:
            print("Fuera de rango.")
            return None
    except ValueError:
        print("Entrada inválida.")
        return None

def recibir_mensajes(cliente, tamaño):
    while True:
        try:
            mensaje = cliente.recv(BUFFER).decode()
            if not mensaje:
                break
            if mensaje.startswith("Turno") or mensaje.startswith("Ganador") or mensaje.startswith("Empate") or mensaje.startswith("Jugador") or mensaje.startswith("Fuera") or mensaje.startswith("Casilla") or mensaje.startswith("¡Es tu turno!") or mensaje.startswith("Esperando"):
                print("\n[Servidor]:", mensaje)
            else:
                tablero = list(mensaje)
                mostrar_tablero(tablero, tamaño)
        except:
            break

def validar_modulo_fecha():
    while True:
        try:
            fecha = input("Ingresa tu fecha de nacimiento (DD-MM-AAAA): ")
            nacimiento = datetime.strptime(fecha, "%d-%m-%Y")
            referencia = datetime(2025, 3, 10)
            dias = (referencia - nacimiento).days
            if dias % 3 == 1:
                print(f"\n¡Tu juego es GATO! ({dias} días desde tu nacimiento)\n")
                break
            else:
                print("No es módulo 1. Intenta con otra fecha.\n")
        except ValueError:
            print("Formato inválido. Usa DD-MM-AAAA.\n")

def main():
    ip = input("Ingresa la IP del servidor: ")
    try:
        puerto = int(input("Ingresa el puerto (ej. 65432): "))
    except:
        puerto = 65432
        print("Puerto inválido. Se usará 65432 por defecto.")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
        cliente.connect((ip, puerto))
        print("Conectado al servidor.")
        print("\nSe usa TCP para mantener el orden y evitar pérdida de datos.\n")

        # Recibir mensaje inicial completo ("Jugador #1" o "Jugador #N")
        mensajes = ""
        while True:
            parte = cliente.recv(BUFFER).decode()
            mensajes += parte
            if "Jugador #" in mensajes:
                break

        print("[Servidor]:", mensajes.strip())

        # Si eres el primer jugador, validar fecha y enviar tamaño del tablero
        if "Jugador #1" in mensajes:
            validar_modulo_fecha()
            while True:
                tamaño = input("Selecciona el tamaño del tablero (3 o 5): ")
                if tamaño in ["3", "5"]:
                    cliente.sendall(tamaño.encode())
                    tamaño = int(tamaño)
                    break
                else:
                    print("Opción inválida.\n")
        else:
            tamaño = None

        tablero_data = cliente.recv(BUFFER).decode()
        tablero = list(tablero_data)
        tamaño = int(len(tablero) ** 0.5)
        mostrar_tablero(tablero, tamaño)

        # Hilo para escuchar actualizaciones
        hilo_escucha = threading.Thread(target=recibir_mensajes, args=(cliente, tamaño), daemon=True)
        hilo_escucha.start()

        while True:
            try:
                turno_msg = cliente.recv(BUFFER).decode()
                if "¡Es tu turno!" in turno_msg:
                    print("\n[Servidor]: ¡Es tu turno!\n")
                    while True:
                        jugada = pedir_jugada(tamaño)
                        if jugada:
                            cliente.sendall(jugada.encode())
                            break
            except:
                print("Conexión cerrada.")
                break

if __name__ == "__main__":
    main()
