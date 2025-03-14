import socket

HOST = "localhost"
PORT = 65432
BUFFER = 1024

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
        return f"{fila},{columna}"
    except ValueError:
        print("Error: Solo se permiten números.")
        return None

# Función principal
def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
        cliente.connect((HOST, PORT))
        print("Conectado al servidor.")

        tamaño = seleccionar_tamaño()
        cliente.sendall(str(tamaño).encode())

        tablero = cliente.recv(BUFFER).decode()
        mostrar_tablero(tablero, tamaño)

        while True:
            jugada = pedir_jugada(tamaño)
            if jugada is None:
                continue

            cliente.sendall(jugada.encode())

            respuesta = cliente.recv(BUFFER).decode()

            if respuesta == "Fuera de rango":
                print("La jugada está fuera del tablero.")
                continue
            elif respuesta == "Casilla ocupada":
                print("Esa casilla ya está ocupada.")
                continue
            elif respuesta in ["Ganaste", "Perdiste", "Empate"]:
                tablero_final = cliente.recv(BUFFER).decode()
                mostrar_tablero(tablero_final, tamaño)
                print(respuesta)
                break
            else:
                mostrar_tablero(respuesta, tamaño)

if __name__ == "__main__":
    main()