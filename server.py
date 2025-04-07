import socket
import threading
import json

HOST = "localhost"
PORT = 65432
BUFFER = 1024
MAX_JUGADORES = 2

clientes = []
hilos = []
lock_tablero = threading.Lock()
lock_conexiones = threading.Lock()
tamaño = None
tablero = []

# Función para crear un tablero vacío
def crear_tablero(tam):
    tablero = [None] * (tam * tam)
    for i in range(tam * tam):
        tablero[i] = ' '
    return tablero

# Función para mostrar el tablero
def mostrar_tablero(tablero, tam):
    print("\nTABLERO ACTUAL")
    print("   ", end="")
    for i in range(tam):
        print(i, end=" ")
    print()

    for i in range(tam):
        print(i, end=" |")
        for j in range(tam):
            print(tablero[i * tam + j], end="|")
        print()
    print()

# Función para colocar un símbolo en el tablero
def colocar_simbolo(tablero, fila, columna, simbolo, tam):
    tablero[fila * tam + columna] = simbolo
    return tablero

# Función para verificar si hay un ganador
def ganador(tablero, simbolo, tam):
    # Verificar filas
    for i in range(tam):
        if all(tablero[i * tam + j] == simbolo for j in range(tam)):
            return True
    # Verificar columnas
    for j in range(tam):
        if all(tablero[i * tam + j] == simbolo for i in range(tam)):
            return True
    # Verificar diagonal principal
    if all(tablero[i * tam + i] == simbolo for i in range(tam)):
        return True
    # Verificar diagonal secundaria
    if all(tablero[i * tam + (tam - 1 - i)] == simbolo for i in range(tam)):
        return True
    return False

# Función para verificar si hay un empate
def empate(tablero):
    return " " not in tablero

# Enviar mensaje a todos los jugadores
def broadcast(diccionario):
    with lock_conexiones:
        for c in clientes:
            try:
                c.sendall(json.dumps(diccionario).encode())
            except:
                continue

# Función para manejar la lógica de cada cliente
def manejar_cliente(cliente, addr, simbolo, es_primero):
    global tamaño, tablero
    try:
        if es_primero:
            # El primer jugador define el tamaño del tablero
            cliente.sendall(json.dumps({"tipo": "solicitar_tamano"}).encode())
            tam_msg = json.loads(cliente.recv(BUFFER).decode())
            tamaño = int(tam_msg["valor"])
            tablero = crear_tablero(tamaño)
            broadcast({"tipo": "mensaje", "contenido": f"Tamaño del tablero: {tamaño}x{tamaño}"})
        else:
            while tamaño is None:
                pass  # espera a que el primero defina el tamaño

        cliente.sendall(json.dumps({"tipo": "simbolo", "valor": simbolo}).encode())
        cliente.sendall(json.dumps({"tipo": "tablero", "estado": tablero}).encode())

        while True:
            data = cliente.recv(BUFFER).decode()
            if not data:
                break
            mensaje = json.loads(data)

            if mensaje["tipo"] == "jugada":
                fila, columna = mensaje["fila"], mensaje["columna"]

                with lock_tablero:
                    index = fila * tamaño + columna
                    if fila < 0 or fila >= tamaño or columna < 0 or columna >= tamaño:
                        cliente.sendall(json.dumps({"tipo": "error", "mensaje": "Fuera de rango"}).encode())
                        continue
                    if tablero[index] != ' ':
                        cliente.sendall(json.dumps({"tipo": "error", "mensaje": "Casilla ocupada"}).encode())
                        continue

                    tablero = colocar_simbolo(tablero, fila, columna, simbolo, tamaño)
                    mostrar_tablero(tablero, tamaño)
                    broadcast({"tipo": "tablero", "estado": tablero})

                    if ganador(tablero, simbolo, tamaño):
                        broadcast({"tipo": "ganador", "simbolo": simbolo})
                        break
                    if empate(tablero):
                        broadcast({"tipo": "empate"})
                        break

    finally:
        with lock_conexiones:
            if cliente in clientes:
                clientes.remove(cliente)
        cliente.close()
        print(f"Cliente {addr} desconectado")

# Función principal que inicia el servidor
def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.bind((HOST, PORT))
        servidor.listen()
        print(f"Servidor esperando {MAX_JUGADORES} jugadores...")

        jugador_actual = 0
        while jugador_actual < MAX_JUGADORES:
            cliente, addr = servidor.accept()
            print(f"Conectado: {addr}")
            with lock_conexiones:
                clientes.append(cliente)

            simbolo = ['X', 'O', 'Z', 'Y'][jugador_actual]
            hilo = threading.Thread(
                target=manejar_cliente,
                args=(cliente, addr, simbolo, jugador_actual == 0)
            )
            hilos.append(hilo)
            hilo.start()
            jugador_actual += 1

        for hilo in hilos:
            hilo.join()

        print("Juego terminado. Servidor cerrado.")

if __name__ == "__main__":
    main()
