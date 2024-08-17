import socket
import threading 
import argparse
import signal
import sys

class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


open_sockets= []

# Definimos la acción que ocurrirá cuando hagamos Ctrl + C
def def_handler(sig, frame):
    print(f"\n {color.RED}[!] Saliendo... {color.END}")

    # Cerramos los sockets que quedaron abiertos durante el escaneo
    for socket in open_sockets:
        socket.close()

    sys.exit(1)


signal.signal(signal.SIGINT, def_handler) #Ctrl + C


# Trabajamos con los datos necesarios como argumentos
# Con esta librería, el valor de los argumentos se almacena como una instancia de la clase options

def get_arguments():
    parser = argparse.ArgumentParser(description="Fast TCP Port Scan")

    # | modo de llamada / donde se almacena el valor / Requerido /Descripción |
    parser.add_argument("-t", "--target", dest="target", required=True, help= "Target's Ip to scan (Ex: -t 192.168.1.2)")

    # | modo de llamada / donde se almacena el valor / Requerido / Descripción |
    parser.add_argument("-p", "--port", dest="port", required=True, help= "Port range to scan (Ex: -p )")
    options = parser.parse_args()

    return options.target, options.port


def create_socket():

    # Socket para direcciones IPv4 y conexiones TPC
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #Tiempo máximo de espera para la conexión.
    s.settimeout(0.5)

    open_sockets.append(s)
    return s

def port_scanner(port, host):

    s = create_socket()

    # Conexión a un host por un puerto, de forma que si esta abierto, la conexión se realiza.
    try:
        s.connect((host, port))
        print(f"[+] Port {port} -{color.GREEN} OPEN {color.END}")

    # Manejamos la opción de que tarde más de lo deseado en realizar la conexión
    except (socket.timeout, ConnectionRefusedError):
        pass

    finally:
        s.close()

    s.close()

def scan_ports(ports, target):

    threads = []

    # Escanea los puertos segun los recibidos en la función "parse_ports"
    for port in ports:
        thread = threading.Thread(target=port_scanner, args=(port, target))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

def parse_ports(ports_str):

    # Trabajamos con los puertos recibidos para que python los interprete correctamente segun lo deseado

    if "-" in ports_str: # Rango de puertos / Asignamos una variable a cada estremo del rango y devolvemos el método "in range()"
        start, end = map(int, ports_str.split("-"))
        return range(start, end+1)
    
    elif "," in ports_str: # varios puertos / Convertimos los puertos a una lista tras separarlos por cada ,
        return map(int, ports_str.split(","))
    
    else: # Un solo puerto / Convertimos ese único puerto a una lista
        return [int(ports_str)]
    

# Función principal
def main():
    # Obtemenos los datos de los argumentos
    target, ports_str = get_arguments()
    ports =  parse_ports(ports_str)
    # Escaneo
    scan_ports(ports, target)


if __name__ == "__main__":
    main()