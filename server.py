import socket
import threading
import random

BUFFER = 1024
HOST = "localhost"
PORT = 65432

clientes = []
hilos = []
lock = threading.Lock()
turno_actual = 0
tamaño_tablero = None
tablero = None

def crear_tablero(tamaño):
    return [' '] * (tamaño * tamaño)

def mostrar_tablero(tablero, tamaño):
    print("\nTABLERO CENTRAL")
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

def colocar_simbolo(tablero, fila, columna, simbolo, tamaño):
    tablero[fila * tamaño + columna] = simbolo

def ganador(tablero, simbolo, tamaño):
    for i in range(tamaño):
        if all(tablero[i * tamaño + j] == simbolo for j in range(tamaño)):
            return True
    for j in range(tamaño):
        if all(tablero[i * tamaño + j] == simbolo for i in range(tamaño)):
            return True
    if all(tablero[i * tamaño + i] == simbolo for i in range(tamaño)):
        return True
    if all(tablero[i * tamaño + (tamaño - 1 - i)] == simbolo for i in range(tamaño)):
        return True
    return False

def empate(tablero):
    return all(c != ' ' for c in tablero)

def jugada_servidor(tablero, tamaño):
    vacias = [i for i, val in enumerate(tablero) if val == ' ']
    return divmod(random.choice(vacias), tamaño)

def enviar_a_todos(mensaje):
    for c in clientes:
        try:
            c.sendall(mensaje.encode())
        except:
            continue

def manejar_cliente(cliente, idx):
    global turno_actual, tablero, tamaño_tablero

    cliente.sendall(f"Jugador #{idx + 1}".encode())
    cliente.sendall("".join(tablero).encode())

    while True:
        try:
            cliente.sendall("Esperando tu turno...".encode())
            while True:
                with lock:
                    if idx == turno_actual:
                        cliente.sendall("¡Es tu turno!".encode())
                        break

            data = cliente.recv(BUFFER).decode()
            if not data:
                break

            fila, columna = int(data[0]), int(data[1])
            mensaje = ""

            with lock:
                if fila < 0 or fila >= tamaño_tablero or columna < 0 or columna >= tamaño_tablero:
                    mensaje = "Fuera de rango"
                elif tablero[fila * tamaño_tablero + columna] != ' ':
                    mensaje = "Casilla ocupada"
                else:
                    colocar_simbolo(tablero, fila, columna, 'X', tamaño_tablero)
                    mostrar_tablero(tablero, tamaño_tablero)
                    if ganador(tablero, 'X', tamaño_tablero):
                        mensaje = f"Jugador #{idx + 1} ganó"
                        enviar_a_todos(mensaje)
                        enviar_a_todos("".join(tablero))
                        return
                    elif empate(tablero):
                        mensaje = "Empate"
                        enviar_a_todos(mensaje)
                        enviar_a_todos("".join(tablero))
                        return
                    else:
                        enviar_a_todos("".join(tablero))
                        enviar_a_todos("Turno del servidor")
                        fila_cpu, col_cpu = jugada_servidor(tablero, tamaño_tablero)
                        colocar_simbolo(tablero, fila_cpu, col_cpu, 'O', tamaño_tablero)
                        mostrar_tablero(tablero, tamaño_tablero)
                        if ganador(tablero, 'O', tamaño_tablero):
                            mensaje = "El servidor (CPU) ganó"
                            enviar_a_todos(mensaje)
                            enviar_a_todos("".join(tablero))
                            return
                        elif empate(tablero):
                            mensaje = "Empate"
                            enviar_a_todos(mensaje)
                            enviar_a_todos("".join(tablero))
                            return
                        else:
                            enviar_a_todos("".join(tablero))

            turno_actual = (turno_actual + 1) % len(clientes)
        except:
            break

    with lock:
        if cliente in clientes:
            clientes.remove(cliente)
    cliente.close()

def main():
    global tamaño_tablero, tablero
    max_jugadores = int(input("¿Cuántos jugadores aceptarás?: "))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.bind((HOST, PORT))
        servidor.listen()
        print("[+] Servidor esperando conexiones...")

        # 🔵 PRIMER CLIENTE
        cliente, addr = servidor.accept()
        print(f"[Jugador 1] Conectado desde {addr}")
        clientes.append(cliente)

        # Enviar su rol
        cliente.sendall("Jugador #1".encode())

        # Esperar tamaño del tablero
        print("[Servidor] Esperando tamaño del tablero del jugador 1...")
        tamaño_tablero = int(cliente.recv(BUFFER).decode())
        print(f"[Servidor] Tamaño recibido: {tamaño_tablero}")

        tablero = crear_tablero(tamaño_tablero)

        hilo = threading.Thread(target=manejar_cliente, args=(cliente, 0))
        hilos.append(hilo)
        hilo.start()

        # 🔵 RESTO DE LOS JUGADORES
        while len(clientes) < max_jugadores:
            cliente, addr = servidor.accept()
            print(f"[Jugador {len(clientes)+1}] Conectado desde {addr}")
            clientes.append(cliente)
            idx = len(clientes) - 1
            hilo = threading.Thread(target=manejar_cliente, args=(cliente, idx))
            hilos.append(hilo)
            hilo.start()

        print("[Servidor] Todos los jugadores están listos. ¡El juego ha comenzado!\n")

        # Esperar a que termine la partida
        for h in hilos:
            h.join()

        print("[*] Partida finalizada.")

if __name__ == "__main__":
    main()
