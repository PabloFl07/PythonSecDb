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

# Define what will occur when we input Ctrl_C
def def_handler(sig, frame):
    print(f"\n {color.RED}[!] Saliendo... {color.END}")

    # Close the sockets that are still open
    for socket in open_sockets:
        socket.close()

    sys.exit(1)


signal.signal(signal.SIGINT, def_handler) #Ctrl + C


# We work with the necessary data as arguments
# With this library, the value of the arguments is stored as an instance of the class options

def get_arguments():
    parser = argparse.ArgumentParser(description="Fast TCP Port Scan")

    # | Call mode / Where the value is stored / Required / Description |
    parser.add_argument("-t", "--target", dest="target", required=True, help= "Target's Ip to scan (Ex: -t 192.168.1.2)")

    # | Call mode / Where the value is stored / Required / Description |
    parser.add_argument("-p", "--port", dest="port", required=True, help= "Port range to scan (Ex: -p )")
    options = parser.parse_args()

    return options.target, options.port


def create_socket():

    # Socket for IPv4 directions and TPC conections
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #Maximum waiting time for connection.
    s.settimeout(0.5)

    open_sockets.append(s)
    return s

def port_scanner(port, host):

    s = create_socket()

    # Connection to a host through a port, so that if it is open, the connection is made.
    try:
        s.connect((host, port))
        print(f"[+] Port {port} -{color.GREEN} OPEN {color.END}")

    # We handle the option of taking longer than desired to make the connection.
    except (socket.timeout, ConnectionRefusedError):
        pass

    finally:
        s.close()

    s.close()

def scan_ports(ports, target):

    threads = []

    # Scan ports as received in the function “parse_ports”.
    for port in ports:
        thread = threading.Thread(target=port_scanner, args=(port, target))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

def parse_ports(ports_str):

    # We work with the received ports so that python interprets them correctly according to what we want.

    if "-" in ports_str: # Port range / We assign a variable to each end of the range and return the method “in range()”.
        start, end = map(int, ports_str.split("-"))
        return range(start, end+1)
    
    elif "," in ports_str: # Several ports / We convert the ports to a list after separating them by each ”,”
        return map(int, ports_str.split(","))
    
    else: # A single port / We convert that single port to a list
        return [int(ports_str)]
    

# Main function
def main():
    # Gets us the data of the arguments
    target, ports_str = get_arguments()
    ports =  parse_ports(ports_str)
    # Scan
    scan_ports(ports, target)


if __name__ == "__main__":
    main()