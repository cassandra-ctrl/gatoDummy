

import socket
import random

# Constantes
HOST = "localhost"
PORT = 65432
BUFFER = 1024

# Crear tablero vacío
def crear_tablero(filas, columnas):
    return "\n".join([",".join([" "]*columnas) for _ in range(filas)])

# Mostrar tablero
def mostrar_tablero(tablero_str):
    filas = tablero_str.split("\n")
    tamaño = len(filas)
    print("\nTABLERO ACTUAL")
    print("   " + " ".join(str(i) for i in range(tamaño)))
    for i, fila in enumerate(filas):
        print(f"{i} |" + "|".join(fila.split(",")) + "|")
    print()

# Colocar símbolo en el tablero
def colocar_simbolo(tablero_str, fila, columna, simbolo):
    tablero = tablero_str.split("\n")
    fila_datos = tablero[fila].split(",")
    fila_datos[columna] = simbolo
    tablero[fila] = ",".join(fila_datos)
    return "\n".join(tablero)

# Verificar ganador
def hay_ganador(tablero_str, simbolo):
    tablero = tablero_str.split("\n")
    tamaño = len(tablero)

    for fila in tablero:
        if all(celda == simbolo for celda in fila.split(",")):
            return True

    for col in range(tamaño):
        if all(fila.split(",")[col] == simbolo for fila in tablero):
            return True

    if all(tablero[i].split(",")[i] == simbolo for i in range(tamaño)):
        return True
    if all(tablero[i].split(",")[tamaño - 1 - i] == simbolo for i in range(tamaño)):
        return True

    return False

# Verificar empate
def es_empate(tablero_str):
    for fila in tablero_str.split("\n"):
        if " " in fila.split(","):
            return False
    return True

# Jugada aleatoria del servidor
def jugada_servidor(tablero_str):
    tablero = tablero_str.split("\n")
    vacias = []
    for i in range(len(tablero)):
        fila = tablero[i].split(",")
        for j in range(len(fila)):
            if fila[j] == " ":
                vacias.append((i, j))
    return random.choice(vacias)

# Programa principal
def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.bind((HOST, PORT))
        servidor.listen()
        print("Servidor en espera...")

        cliente, addr = servidor.accept()
        with cliente:
            print(f"Cliente conectado desde {addr}")

            tamaño = cliente.recv(BUFFER).decode()
            filas = columnas = int(tamaño)

            tablero = crear_tablero(filas, columnas)
            mostrar_tablero(tablero)
            cliente.sendall(tablero.encode())

            while True:
                data = cliente.recv(BUFFER).decode()
                if not data:
                    break

                fila, columna = map(int, data.split(","))
                celdas = tablero.split("\n")

                if fila < 0 or fila >= filas or columna < 0 or columna >= columnas:
                    cliente.sendall("Fuera de rango".encode())
                    continue
                if celdas[fila].split(",")[columna] != " ":
                    cliente.sendall("Casilla ocupada".encode())
                    continue

                tablero = colocar_simbolo(tablero, fila, columna, "X")
                mostrar_tablero(tablero)

                if hay_ganador(tablero, "X"):
                    cliente.sendall("Ganaste".encode())
                    cliente.sendall(tablero.encode())
                    print("Cliente ganó.")
                    break
                if es_empate(tablero):
                    cliente.sendall("Empate".encode())
                    cliente.sendall(tablero.encode())
                    print("Empate.")
                    break

                print("Turno del servidor...")
                fila_cpu, col_cpu = jugada_servidor(tablero)
                tablero = colocar_simbolo(tablero, fila_cpu, col_cpu, "O")
                mostrar_tablero(tablero)

                if hay_ganador(tablero, "O"):
                    cliente.sendall("Perdiste".encode())
                    cliente.sendall(tablero.encode())
                    print("Servidor ganó.")
                    break
                if es_empate(tablero):
                    cliente.sendall("Empate".encode())
                    cliente.sendall(tablero.encode())
                    print("Empate.")
                    break

                cliente.sendall(tablero.encode())

if __name__ == "__main__":
    main()
