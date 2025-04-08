import socket
from datetime import datetime

HOST = "localhost"
PORT = 65432
BUFFER = 1024

# Función para mostrar tablero
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

# Función para seleccionar el tamaño del tablero
def seleccionar_tamaño():
    while True:
        tamaño = input("Selecciona el tamaño del tablero (3 o 5): ")
        if tamaño in ["3", "5"]:
            return int(tamaño)
        print("Opción inválida. Intenta de nuevo.")

# Función para pedir la jugada al usuario
def pedir_jugada(tamaño):
    try:
        fila = int(input(f"Ingrese fila (0 a {tamaño-1}): "))
        columna = int(input(f"Ingrese columna (0 a {tamaño-1}): "))
        if 0 <= fila < tamaño and 0 <= columna < tamaño:
            return [fila, columna]
        else:
            print("Error: La fila y columna deben estar dentro del rango.")
            return None
    except ValueError:
        print("Error: Solo se permiten números.")
        return None

# Función para calcular días y validar módulo
def validar_modulo_fecha():
    while True:
        try:
            fecha_nacimiento = input("Ingresa tu fecha de nacimiento (formato DD-MM-AAAA): ")
            fecha_nacimiento_dt = datetime.strptime(fecha_nacimiento, "%d-%m-%Y")
            fecha_referencia = datetime(2025, 3, 10)
            dias = (fecha_referencia - fecha_nacimiento_dt).days
            modulo = dias % 3
            print(f"\nDías desde tu nacimiento hasta el 10 de marzo de 2025: {dias} días")
            print(f"Días % 3 = {modulo}")
            if modulo == 1:
                print("\n¡Tu juego es GATO! Iniciando partida...\n")
                break
            else:
                print("\nNo es módulo 1. Debes ingresar otra fecha de nacimiento.\n")
        except ValueError:
            print("Formato inválido. Usa DD-MM-AAAA.\n")

# Función principal
def main():
    validar_modulo_fecha()
    ip=input("Ingresa la IP del servidor: ")
    try:
        puerto = int(input("Ingresa el puerto del servidor (ejemplo: 65432): "))
    except ValueError:
        print("Puerto inválido. Usando 65432 por defecto.")
        port = 65432
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
        cliente.connect((ip, puerto))
        print("Conectado al servidor.")
        print("\n Se usó el protocolo TCP porque garantiza que los mensajes lleguen en orden y sin pérdidas,")
        print("y evita que se desincronice el juego entre el cliente y el servidor.\n")
        tamaño = seleccionar_tamaño()
        cliente.sendall(str(tamaño).encode())

        # Recibir tablero inicial
        tablero = list(cliente.recv(BUFFER).decode())
        mostrar_tablero(tablero, tamaño)
        inicio_partida = datetime.now()

        while True:
            jugada = pedir_jugada(tamaño)
            if jugada is None:
                continue

            # Enviar jugada
            cliente.sendall(f"{jugada[0]}{jugada[1]}".encode())

            respuesta = cliente.recv(BUFFER).decode().strip() 

            if respuesta == "Fuera de rango":
                print("La jugada está fuera del tablero.")
                continue
            elif respuesta == "Casilla ocupada":
                print("Esa casilla ya está ocupada.")
                continue
            elif respuesta == "Ganaste":
                print("¡Ganaste!")
                tablero = list(cliente.recv(BUFFER).decode())
                mostrar_tablero(tablero, tamaño)
                break
            elif respuesta == "Perdiste":
                print("Perdiste.")
                tablero = list(cliente.recv(BUFFER).decode())
                mostrar_tablero(tablero, tamaño)
                break  
            elif respuesta == "Empate":
                print("Empate.")
                tablero = list(cliente.recv(BUFFER).decode())
                mostrar_tablero(tablero, tamaño)
                break
            elif respuesta == "Continuar":
                tablero = list(cliente.recv(BUFFER).decode())
                mostrar_tablero(tablero, tamaño)

        fin_partida = datetime.now()
        duracion = fin_partida - inicio_partida
        print(f"\n Tiempo total de la partida: {duracion}segundos")

if __name__ == "__main__":
    main()
