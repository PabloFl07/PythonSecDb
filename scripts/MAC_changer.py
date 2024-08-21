''' README
This script changes your MAC address or restores it to the permanent one.
It uses "subprocess" to execute bash commands to do these tasks, in addition to handling the "stout" and "stderr" to display error messages or hide them.
To verify the MAC given so that is compatible, it uses the library "re" to filter the MAC with a regular expression.
To restore the MAC, just use the parametre "--restore" and add anything so that it has a value
'''
import argparse , re , subprocess, sys , signal

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

# Define what will occur when we input Ctrl + C
def def_handler(sig, frame):
    print(f"\n {color.RED}[!] Exiting... {color.END}")
    sys.exit(1)

signal.signal(signal.SIGINT, def_handler) #Ctrl + C

def get_arguments():
    parser = argparse.ArgumentParser(description="Tool for changing a network interface MAC address")

    # Argument definitions
    parser.add_argument("-i", "--interface", dest="interface", required=True, help= "Name of the network interface")
    parser.add_argument("-m", "--mac", dest="mac_address", required=False, help= "New MAC for the network interface")
    parser.add_argument("--restore", dest="restore", required=False, help= "Return to the original MAC address")
    
    arguments = parser.parse_args()

    return arguments.interface, arguments.mac_address, arguments.restore

def isvalid(interface, mac_address):
    # Looks for your system network interfaces
    check_interfaces = subprocess.run("ip a | grep -oE '^[0-9]+: [^:]+' | awk '{print $2}'", shell=True, capture_output=True, text=True)
    # Store the interfaces in a list for its management
    available_interfaces = check_interfaces.stdout.split()
    if interface in available_interfaces:
        if mac_address: # Checks if a MAC has been given
            is_valid = re.match(r'^([A-Fa-f0-9]{2}[:]){5}[A-Fa-f0-9]{2}$', mac_address) # Looks for a match in the estructure of the MAC given
            return is_valid
        else: # If not, one will be assigned
            return is_valid
    else:
        print(f"\n{color.YELLOW}[!] Network interface has not been found on your system.{color.END}")
        sys.exit(1)

def change_mac_address(interface, mac_address):
    if not mac_address:
        mac_address = "f0:a2:25:01:02:03"
    if isvalid(interface, mac_address):
        subprocess.run(["ifconfig", interface, "down"]) # Set the interface down
        try:
            result = subprocess.run(["ifconfig", interface, "hw", "ether", mac_address], capture_output=True, text=True) # Change MAC address
            
            if result.returncode != 0: 
                error_message = result.stderr.strip() if result.stderr else "Unknown error" # We make sure that we show the error message
                print(f"\n{color.RED}[!] Error while changing MAC: {color.END}{error_message}")
                sys.exit(1)
        except PermissionError:
            sys.exit(1)  

        subprocess.run(["ifconfig", interface , "up"]) # Set the interface up

        print(f"\n{color.YELLOW}[+]{color.END} MAC address succesfully changed to: {color.BLUE}{mac_address}{color.END}")
    else:
        print(f"\n{color.RED}[!] There's something wrong with the inputed MAC{color.END}") 

def restore_mac(interface):
    # Get the Permanent MAC of your computer.
    get_original_mac = subprocess.run("macchanger ens32 | grep 'Permanent MAC:' | awk '{print $3}'", shell=True, capture_output=True, text=True)
    original_mac = get_original_mac.stdout

    subprocess.run(["macchanger", "-p", "ens32"], capture_output=True, text=True) # Restore the MAC

    # Get the MAC AFTER the change for comparing.
    get_current_mac = subprocess.run("macchanger ens32 | grep 'Current MAC:' | awk '{print $3}'", shell=True, capture_output=True, text=True)
    current_mac = get_current_mac.stdout

    if original_mac == current_mac: # Check if the MAC has been restored correctly
        print(f"\n{color.YELLOW}[+]{color.END} MAC restored to the original: {color.GREEN}{original_mac}{color.END}")
    else:
        print(f"\n{color.RED}[!]{color.END} An error has occurred while restoring the MAC address: \n{color.RED}Current MAC: {current_mac}{color.END} |\n{color.BLUE} {original_mac}{color.END}")

def main():
    interface, mac_address, restore= get_arguments() # Store the arguments as variables
    if restore: 
        restore_mac(interface)
    else:
        change_mac_address(interface, mac_address)

if __name__ == "__main__":
    main()