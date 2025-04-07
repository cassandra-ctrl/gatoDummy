import socket
import json

HOST = "localhost"
PORT = 65432
BUFFER = 1024

# Función para mostrar el tablero sin usar join ni split
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

# Función para pedir la jugada al usuario
def pedir_jugada(tamaño):
    try:
        fila = int(input(f"Ingrese fila (0 a {tamaño-1}): "))
        columna = int(input(f"Ingrese columna (0 a {tamaño-1}): "))
        return {"tipo": "jugada", "fila": fila, "columna": columna}
    except ValueError:
        print("Error: Solo se permiten números.")
        return None

# Función principal
def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
        cliente.connect((HOST, PORT))
        simbolo = None
        tamaño = None
        tablero = []

        while True:
            data = cliente.recv(BUFFER).decode()
            if not data:
                print("Conexión cerrada por el servidor.")
                break

            mensaje = json.loads(data)

            if mensaje["tipo"] == "solicitar_tamano":
                while True:
                    tam = input("Selecciona el tamaño del tablero (3 o 5): ")
                    if tam in ["3", "5"]:
                        cliente.sendall(json.dumps({"tipo": "tamano", "valor": int(tam)}).encode())
                        break
                    else:
                        print("Opción inválida. Intenta de nuevo.")

            elif mensaje["tipo"] == "simbolo":
                simbolo = mensaje["valor"]
                print(f"Tu símbolo es: {simbolo}")

            elif mensaje["tipo"] == "mensaje":
                print(mensaje["contenido"])

            elif mensaje["tipo"] == "tablero":
                tablero = mensaje["estado"]
                tamaño = int(len(tablero) ** 0.5)
                mostrar_tablero(tablero, tamaño)

            elif mensaje["tipo"] == "error":
                print(mensaje["mensaje"])

            elif mensaje["tipo"] == "ganador":
                mostrar_tablero(tablero, tamaño)
                if mensaje["simbolo"] == simbolo:
                    print("¡Ganaste!")
                else:
                    print(f"El jugador con símbolo {mensaje['simbolo']} ganó.")
                break

            elif mensaje["tipo"] == "empate":
                mostrar_tablero(tablero, tamaño)
                print("¡Empate!")
                break

            # Después de recibir tablero actualizado, solicitar jugada
            if simbolo and tamaño and mensaje["tipo"] == "tablero":
                jugada = pedir_jugada(tamaño)
                if jugada:
                    cliente.sendall(json.dumps(jugada).encode())

if __name__ == "__main__":
    main()
