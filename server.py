import socket
import random

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
    print("   " + " ".join(str(i) for i in range(tamaño)))
    for i in range(tamaño):
        print(f"{i} |", end="")
        for j in range(tamaño):
            print(tablero[i * tamaño + j], end="|")
        print()
    print()

# Función para colocar un símbolo en el tablero
def colocar_simbolo(tablero, fila, columna, simbolo, tamaño):
    tablero[fila * tamaño + columna] = simbolo
    return tablero

# Función para verificar si hay un ganador
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
    vacias = [i for i, val in enumerate(tablero) if val == " "]
    return divmod(random.choice(vacias), tamaño)

# Función principal
def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.bind((HOST, PORT))
        servidor.listen()
        print("Servidor en espera...")

        cliente, addr = servidor.accept()
        with cliente:
            print(f"Cliente conectado desde {addr}")

            tamaño = int(cliente.recv(BUFFER).decode())
            tablero = crear_tablero(tamaño)
            mostrar_tablero(tablero, tamaño)
            cliente.sendall("".join(tablero).encode())

            while True:
                data = cliente.recv(BUFFER).decode()
                if not data:
                    break

                fila, columna = map(int, data.split(","))
                if fila < 0 or fila >= tamaño or columna < 0 or columna >= tamaño:
                    cliente.sendall("Fuera de rango".encode())
                    continue
                if tablero[fila * tamaño + columna] != " ":
                    cliente.sendall("Casilla ocupada".encode())
                    continue

                tablero = colocar_simbolo(tablero, fila, columna, "X", tamaño)
                mostrar_tablero(tablero, tamaño)

                if ganador(tablero, "X", tamaño):
                    cliente.sendall("Ganaste".encode())
                    cliente.sendall("".join(tablero).encode())
                    print("Cliente ganó.")
                    break
                if empate(tablero):
                    cliente.sendall("Empate".encode())
                    cliente.sendall("".join(tablero).encode())
                    print("Empate.")
                    break

                print("Turno del servidor...")
                fila_cpu, col_cpu = jugada_servidor(tablero, tamaño)
                tablero = colocar_simbolo(tablero, fila_cpu, col_cpu, "O", tamaño)
                mostrar_tablero(tablero, tamaño)

                if ganador(tablero, "O", tamaño):
                    cliente.sendall("Perdiste".encode())
                    cliente.sendall("".join(tablero).encode())
                    print("Servidor ganó.")
                    break
                if empate(tablero):
                    cliente.sendall("Empate".encode())
                    cliente.sendall("".join(tablero).encode())
                    print("Empate.")
                    break

                cliente.sendall("".join(tablero).encode())

if __name__ == "__main__":
    main()