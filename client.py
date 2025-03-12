import socket

# Configuración de IP y puerto
IP = input("Ingresa la IP del servidor: ")
PORT = int(input("Ingresa el puerto del servidor: "))

# Creación del socket y conexión
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPClientSocket:
    try:
        TCPClientSocket.connect((IP, PORT))
        
        # Mensaje de bienvenida del servidor
        mensaje = TCPClientSocket.recv(1024).decode()
        print(mensaje)

        # Se selecioona nivel de dificultad y lo enviamos al Server
        nivel = input("Ingresa dificultad de la partida (1= Principiante | 2= Avanzado): ")
        
        # Validar el nivel de dificultad
        if nivel not in ['1', '2']:
            print("Nivel inválido. Debe ser 1 o 2.")
            exit(1)
        
        # Enviamos el nivel al servidor y lo codificamos
        TCPClientSocket.sendall(nivel.encode())

        # Determinar el tamaño del tablero basado en el nivel
        if nivel == '1':
            filas, columnas = 3, 3
        if nivel == '2':
            filas, columnas = 5, 5
        else:
            filas, columnas = 3,3

        while True:
            # Decodificamos el tablero
            tablero = TCPClientSocket.recv(1024).decode()
            print(tablero)

            # Solicitar la jugada al usuario
            try:
                fila = int(input(f"Ingrese fila (0-{filas-1}): "))
                columna = int(input(f"Ingrese columna (0-{columnas-1}): "))
                
                # Validar que la fila y columna estén dentro del rango
                if fila < 0 or fila >= filas or columna < 0 or columna >= columnas:
                    print("Movimiento fuera de rango.")
                    continue
                
                jugada = f"{fila},{columna}"
                
                # Enviamos la jugada al
                TCPClientSocket.sendall(jugada.encode())

                # Respuesta del servidor
                respuesta = TCPClientSocket.recv(1024).decode()
                print(respuesta)

                if respuesta == "fin":
                    print("Juego terminado")
                    break

            except ValueError:
                print("Entrada inválida. Debes ingresar números.")
                continue

    except ConnectionRefusedError:
        print("Error al conectar al servidor")
    #preuba commit