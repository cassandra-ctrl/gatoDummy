# servidor.py
import socket
import random

# Función para crear un tablero vacío como cadena
def crear_tablero(filas, columnas):
    return "\n".join([",".join([" " for _ in range(columnas)]) for _ in range(filas)])

# Función para actualizar el tablero
def actualizar_tablero(tablero, fila, columna, simbolo):
    filas = tablero.split("\n")
    fila_actual = filas[fila].split(",")
    fila_actual[columna] = simbolo
    filas[fila] = ",".join(fila_actual)
    return "\n".join(filas)

# Función para verificar si hay un ganador
def verificar_ganador(tablero, simbolo):
    filas = tablero.split("\n")
    tamaño = len(filas)
    # Verificar filas
    for fila in filas:
        if all(casilla == simbolo for casilla in fila.split(",")):
            return True
    # Verificar columnas
    for columna in range(tamaño):
        if all(fila.split(",")[columna] == simbolo for fila in filas):
            return True
    # Verificar diagonales
    if all(filas[i].split(",")[i] == simbolo for i in range(tamaño)):
        return True
    if all(filas[i].split(",")[tamaño - 1 - i] == simbolo for i in range(tamaño)):
        return True
    return False

# Función para realizar una jugada aleatoria
def jugada_aleatoria(tablero):
    filas = tablero.split("\n")
    casillas_vacias = []
    for i in range(len(filas)):
        for j in range(len(filas)):
            if filas[i].split(",")[j] == " ":
                casillas_vacias.append((i, j))
    return random.choice(casillas_vacias)

# Función para imprimir el tablero con coordenadas
def imprimir_tablero(tablero):
    filas = tablero.split("\n")
    tamaño = len(filas)
    print("Tablero actual:")
    # Imprimir encabezado de columnas
    print("   " + " ".join(str(i) for i in range(tamaño)))
    # Imprimir filas con coordenadas
    for i, fila in enumerate(filas):
        print(f"{i} |" + "|".join(fila.split(",")) + "|")

# Configuración del servidor
HOST = "0.0.0.0"  # Escucha en todas las interfaces
PORT = 12345      # Puerto del servidor

# Crear el socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
    servidor.bind((HOST, PORT))
    servidor.listen(1)
    print(f"Servidor escuchando en {HOST}:{PORT}...")

    # Aceptar conexión del cliente
    cliente, direccion = servidor.accept()
    print(f"Conexión establecida con {direccion}")

    # Recibir la elección del tamaño del tablero del cliente
    tamaño_tablero = cliente.recv(1024).decode()
    if tamaño_tablero == "3":
        filas, columnas = 3, 3
    else:
        filas, columnas = 5, 5

    # Crear tablero inicial
    tablero = crear_tablero(filas, columnas)
    print(f"Tablero inicial ({filas}x{columnas}):")
    imprimir_tablero(tablero)

    # Enviar tablero inicial al cliente
    cliente.sendall(tablero.encode())

    while True:
        # Recibir jugada del cliente
        jugada = cliente.recv(1024).decode()
        fila, columna = map(int, jugada.split(","))

        # Validar jugada
        filas = tablero.split("\n")
        if fila < 0 or fila >= len(filas) or columna < 0 or columna >= len(filas):
            cliente.sendall("Fuera de rango".encode())
            continue
        if filas[fila].split(",")[columna] != " ":
            cliente.sendall("Casilla ocupada".encode())
            continue

        # Actualizar tablero con la jugada del cliente
        tablero = actualizar_tablero(tablero, fila, columna, "X")
        print("Tablero después de la jugada del cliente:")
        imprimir_tablero(tablero)

        # Verificar si el cliente ha ganado
        if verificar_ganador(tablero, "X"):
            cliente.sendall("Ganaste".encode())
            print("El cliente ha ganado.")
            break

        # Turno del servidor (jugada aleatoria)
        print("Turno del servidor...")
        fila, columna = jugada_aleatoria(tablero)
        tablero = actualizar_tablero(tablero, fila, columna, "O")
        print("Tablero después de la jugada del servidor:")
        imprimir_tablero(tablero)

        # Enviar tablero actualizado al cliente
        cliente.sendall(tablero.encode())

        # Verificar si el servidor ha ganado
        if verificar_ganador(tablero, "O"):
            cliente.sendall("Perdiste".encode())
            print("El servidor ha ganado.")
            break

    print("Juego terminado")