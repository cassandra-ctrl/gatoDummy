
import socket
import random
import threading

HOST = "localhost"
PORT = 65432
BUFFER = 1024

# Función para crear un tablero vacío
def crear_tablero(tamaño):
    tablero = [None] * (tamaño * tamaño)

    for i in range(tamaño * tamaño):
        tablero[i] = ' '

    return tablero

# Función para mostrar el tablero
def mostrar_tablero(tablero, tamaño):
    print("\nTABLERO ACTUAL")

    # Imprime encabezado de columnas
    # end: Ya no agrega el salto de linea
    print("   ", end="")
    for i in range(tamaño):
        print(i, end=" ")
    print()

    # Imprime filas
    #i = filas
    #j= columna
    for i in range(tamaño):
        print(i, end=" |")  # Índice de la fila
        for j in range(tamaño):
            print(tablero[i * tamaño + j], end="|")
        print()  # Salto de línea al final de cada fila
    print()  # Salto de línea extra para mejor formato

# Función para colocar un símbolo en el tablero
def colocar_simbolo(tablero, fila, columna, simbolo, tamaño):
    tablero[fila * tamaño + columna] = simbolo
    return tablero

# Función para verificar si hay un ganador
# Función para verificar si un jugador ha ganado
def ganador(tablero, simbolo, tamaño):
    # Verificar filas
    for i in range(tamaño):
        if all(tablero[i * tamaño + j] == simbolo for j in range(tamaño)):
            return True
    # Verificar columnas
    for j in range(tamaño):
        if all(tablero[i * tamaño + j] == simbolo for i in range(tamaño)):
            return True
    # Verificar diagonal principal
    if all(tablero[i * tamaño + i] == simbolo for i in range(tamaño)):
        return True
    # Verificar diagonal secundaria
    if all(tablero[i * tamaño + (tamaño - 1 - i)] == simbolo for i in range(tamaño)):
        return True
    return False

# Función para verificar si hay un empate
def empate(tablero):
    return " " not in tablero

# Función para realizar una jugada aleatoria del servidor
def jugada_servidor(tablero, tamaño):
    vacias = [i for i, val in enumerate(tablero) if val == ' ']
    return divmod(random.choice(vacias), tamaño)

def numero_jugadores():
    jugadores = int(print("Ingrese el numero de jugadores:"))
    hilos = []
    for i in range(jugadores):
        print(f"Creando hilo {i}")
        hilo = threading.Thread(target=colocar_simbolo)
        hilos.append(hilo)
    

# Función principal que maneja la lógica del servidor
def main():
    HOST = '127.0.0.1'  # Dirección del servidor
    PORT = 65432        # Puerto de escucha
    BUFFER = 1024       # Tamaño del buffer para recibir datos
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.bind((HOST, PORT))
        servidor.listen()
        print("Servidor en espera...")

        cliente, addr = servidor.accept()
        with cliente:
            print(f"Cliente conectado desde {addr}")

            # Recibir tamaño del tablero del cliente
            tamaño = int(cliente.recv(BUFFER).decode())
            tablero = crear_tablero(tamaño)
            mostrar_tablero(tablero, tamaño)
            cliente.sendall(bytes(tablero))

            while True:
                # Recibir jugada del cliente
                data = cliente.recv(BUFFER).decode()
                if not data:
                    break

                fila, columna = int(data[0]), int(data[1])
                
                # Verificar si la jugada es válida
                if fila < 0 or fila >= tamaño or columna < 0 or columna >= tamaño:
                    cliente.sendall("Fuera de rango".encode())
                    continue
                if tablero[fila * tamaño + columna] != ' ':
                    cliente.sendall("Casilla ocupada".encode())
                    continue

                # Colocar símbolo del cliente en el tablero
                tablero = colocar_simbolo(tablero, fila, columna, 'X', tamaño)
                mostrar_tablero(tablero, tamaño)

                # Verificar si el cliente ganó
                if ganador(tablero, 'X', tamaño):
                    cliente.sendall("Ganaste".encode())
                    cliente.sendall(bytes(tablero))
                    print("Cliente ganó.")
                    break
                if empate(tablero):
                    cliente.sendall("Empate".encode())
                    cliente.sendall(bytes(tablero))
                    print("Empate.")
                    break

                # Turno del servidor
                print("Turno del servidor...")
                fila_cpu, col_cpu = jugada_servidor(tablero, tamaño)
                tablero = colocar_simbolo(tablero, fila_cpu, col_cpu, 'O', tamaño)
                mostrar_tablero(tablero, tamaño)