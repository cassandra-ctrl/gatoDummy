import socket
import random


BUFFER = 1024
host="localhost"
port=65432

# Función para crear un tablero vacío
def crear_tablero(tamaño):
    return [' '] * (tamaño * tamaño)

# Función para mostrar el tablero
def mostrar_tablero(tablero, tamaño):
    print("\nTABLERO ACTUAL")
    print("   ", end="")
    for i in range(tamaño):
        print(i, end=" ")
    print()
    for i in range(tamaño):
        print(i, end=" |")
        for j in range(tamaño):
            print(tablero[i * tamaño + j], end="|")
        print()
    print()

# Función para colocar un símbolo en el tablero
def colocar_simbolo(tablero, fila, columna, simbolo, tamaño):
    tablero[fila * tamaño + columna] = simbolo
    return tablero

def ganador(tablero, simbolo, tamaño):
    # Verificar filas
    for i in range(tamaño):
        contador = 0
        for j in range(tamaño):
            if tablero[i * tamaño + j] == simbolo:
                contador += 1
        if contador == tamaño:
            return True

    # Verificar columnas
    for j in range(tamaño):
        contador = 0
        for i in range(tamaño):
            if tablero[i * tamaño + j] == simbolo:
                contador += 1
        if contador == tamaño:
                    return True

    # Verificar diagonal principal
    contador = 0
    for i in range(tamaño):
        if tablero[i * tamaño + i] == simbolo:
            contador += 1
    if contador == tamaño:
        return True

    # Verificar diagonal secundaria
    contador = 0
    for i in range(tamaño):
        if tablero[i * tamaño + (tamaño - 1 - i)] == simbolo:
            contador += 1
    if contador == tamaño:
        return True

    return False


def empate(tablero):
    for casilla in tablero:
        if casilla == ' ':
            return False
    return True


# Jugada aleatoria del servidor
def jugada_servidor(tablero, tamaño):
    vacias = [i for i, val in enumerate(tablero) if val == ' ']
    return divmod(random.choice(vacias), tamaño)

# Función principal
def main():


    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.bind((host, port))
        servidor.listen()
        print("Servidor en espera...")

        cliente, addr = servidor.accept()
        with cliente:
            print(f"Cliente conectado desde {addr}")

            # Recibir tamaño del tablero
            tamaño = int(cliente.recv(BUFFER).decode())
            tablero = crear_tablero(tamaño)
            mostrar_tablero(tablero, tamaño)
            cliente.sendall("".join(tablero).encode())

            while True:
                # Recibir jugada del cliente
                data = cliente.recv(BUFFER).decode()
                if not data:
                    break

                fila, columna = int(data[0]), int(data[1])
                mensaje = ""
                tablero_actualizado = None

                # Verificar si la jugada es válida
                if fila < 0 or fila >= tamaño or columna < 0 or columna >= tamaño:
                    mensaje = "Fuera de rango"
                elif tablero[fila * tamaño + columna] != ' ':
                    mensaje = "Casilla ocupada"
                else:
                    # Colocar símbolo del cliente
                    tablero = colocar_simbolo(tablero, fila, columna, 'X', tamaño)
                    mostrar_tablero(tablero, tamaño)

                    # Verificar si el cliente ganó
                    if ganador(tablero, 'X', tamaño):
                        mensaje = "Ganaste"
                        tablero_actualizado = "".join(tablero)
                        print("Cliente ganó.")
                    elif empate(tablero):
                        mensaje = "Empate"
                        tablero_actualizado = "".join(tablero)
                        print("Empate.")
                    else:
                        # Turno del servidor
                        print("Turno del servidor...")
                        fila_cpu, col_cpu = jugada_servidor(tablero, tamaño)
                        tablero = colocar_simbolo(tablero, fila_cpu, col_cpu, 'O', tamaño)
                        mostrar_tablero(tablero, tamaño)

                        # Verificar si el servidor ganó
                        if ganador(tablero, 'O', tamaño):
                            mensaje = "Perdiste"
                            tablero_actualizado = "".join(tablero)
                            print("Servidor ganó.")
                        elif empate(tablero):
                            mensaje = "Empate"
                            tablero_actualizado = "".join(tablero)
                            print("Empate.")
                        else:
                            mensaje = "Continuar"
                            tablero_actualizado = "".join(tablero)

                # Enviar mensaje al cliente
                cliente.sendall(mensaje.encode())

                # Si corresponde, enviar tablero
                if tablero_actualizado:
                    cliente.sendall(tablero_actualizado.encode())

                # Si la partida terminó, salir del bucle
                if mensaje in ["Ganaste", "Perdiste", "Empate"]:
                    break



if __name__ == "__main__":
    main()
