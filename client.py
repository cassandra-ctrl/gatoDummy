# cliente.py
import socket

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

# Configuración del cliente
HOST = input("Ingresa la IP del servidor: ")
PORT = int(input("Ingresa el puerto del servidor: "))

# Crear el socket y conectar al servidor
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
    cliente.connect((HOST, PORT))

    # Elegir el tamaño del tablero
    tamaño = input("Elige el tamaño del tablero (3 para 3x3, 5 para 5x5): ")
    while tamaño not in ["3", "5"]:
        print("Opción inválida. Debe ser 3 o 5.")
        tamaño = input("Elige el tamaño del tablero (3 para 3x3, 5 para 5x5): ")
    cliente.sendall(tamaño.encode())

    # Recibir tablero inicial del servidor
    tablero = cliente.recv(1024).decode()
    imprimir_tablero(tablero)

    while True:
        # Solicitar jugada al usuario
        try:
            fila = int(input(f"Ingresa la fila (0-{int(tamaño)-1}): "))
            columna = int(input(f"Ingresa la columna (0-{int(tamaño)-1}): "))
            jugada = f"{fila},{columna}"
            cliente.sendall(jugada.encode())
        except ValueError:
            print("Entrada inválida. Debes ingresar números.")
            continue

        # Recibir respuesta del servidor
        respuesta = cliente.recv(1024).decode()

        if respuesta == "Fuera de rango":
            print("La casilla está fuera del rango permitido. Intenta de nuevo.")
            continue
        elif respuesta == "Casilla ocupada":
            print("La casilla ya está ocupada. Intenta de nuevo.")
            continue

        # Actualizar tablero local
        tablero = respuesta
        imprimir_tablero(tablero)

        # Verificar si el juego ha terminado
        if respuesta in ["Ganaste", "Perdiste"]:
            print(respuesta)
            break