import sys
import os
import subprocess
import time
import threading
from pathlib import Path
from colorama import init, Fore, Style

init(autoreset=True)

def print_help():
    print(Fore.CYAN + """
[OVPN-BULKER] - Manage OpenVPN Profiles via NetworkManager

Usage:
  main.py <directory> <username> <password>       Import all .ovpn files
  main.py list                                    Show all imported VPNs
  main.py connect <vpn-name>                      Connect to a VPN
  main.py disconnect <vpn-name>                   Disconnect a VPN
  main.py delete-all                              Remove all VPNs
  main.py help                                    Show this message
""")

spinner_running = False

def spin_with_label(label):
    global spinner_running
    arrows = ['↑', '↗', '→', '↘', '↓', '↙', '←', '↖']
    i = 0
    while spinner_running:
        sys.stdout.write(f"\r[{Fore.YELLOW}{arrows[i % 8]}{Style.RESET_ALL}] {label}... ")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write("\r")

def get_all_vpn_names():
    result = subprocess.run(["nmcli", "-t", "-f", "NAME,TYPE", "connection", "show"],
                            capture_output=True, text=True)
    return [line.split(":")[0] for line in result.stdout.strip().split("\n") if ":vpn" in line]

def import_vpn(file_path, username, password):
    name = os.path.splitext(os.path.basename(file_path))[0]
    subprocess.run(["nmcli", "connection", "import", "type", "openvpn", "file", file_path],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["nmcli", "connection", "modify", name, "vpn.user-name", username],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["nmcli", "connection", "modify", name, "+vpn.data", "password-flags=0"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["nmcli", "connection", "modify", name, "vpn.secrets", f"password={password}"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return name

def delete_vpn(name):
    subprocess.run(["nmcli", "connection", "delete", name],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def delete_all_vpns():
    for name in get_all_vpn_names():
        delete_vpn(name)

def connect_vpn(name):
    subprocess.run(["nmcli", "connection", "up", name])

def disconnect_vpn(name):
    subprocess.run(["nmcli", "connection", "down", name])

def set_autoconnect(name, enabled=True):
    flag = "yes" if enabled else "no"
    subprocess.run(["nmcli", "connection", "modify", name, "connection.autoconnect", flag],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def install_all(directory, username, password):
    ovpn_files = list(Path(directory).glob("*.ovpn"))
    if not ovpn_files:
        print(Fore.RED + f"[!] No .ovpn files found in {directory}")
        return

    global spinner_running
    print()
    spinner_running = True
    thread = threading.Thread(target=spin_with_label, args=("Importing OVPN configurations",))
    thread.start()

    for file in ovpn_files:
        name = import_vpn(str(file), username, password)
        set_autoconnect(name, True)

    spinner_running = False
    thread.join()

    print(f"[{Fore.GREEN}✓{Style.RESET_ALL}] Imported {len(ovpn_files)} VPN(s) successfully.\n")

def main():
    args = sys.argv[1:]

    if len(args) == 3 and not args[0].startswith("-"):
        directory, username, password = args
        install_all(directory, username, password)
        return

    if not args or args[0].lower() in ["help", "--help", "-h"]:
        print_help()
        return

    command = args[0].lower()

    if command == "list":
        names = get_all_vpn_names()
        print(Fore.CYAN + "\n[=] VPN Profiles:")
        for name in names:
            print(f"  - {Fore.GREEN}{name}")
        print()

    elif command == "delete-all":
        confirm = input(Fore.YELLOW + "Are you sure you want to delete all VPNs? (y/N): ").lower()
        if confirm == "y":
            global spinner_running
            spinner_running = True
            thread = threading.Thread(target=spin_with_label, args=("Deleting OVPN configurations",))
            thread.start()

            delete_all_vpns()

            spinner_running = False
            thread.join()

            print(f"[{Fore.GREEN}✓{Style.RESET_ALL}] All VPNs deleted.\n")
        else:
            print("Aborted.")

    elif command == "connect" and len(args) == 2:
        connect_vpn(args[1])

    elif command == "disconnect" and len(args) == 2:
        disconnect_vpn(args[1])

    else:
        print(Fore.RED + "[!] Invalid arguments.\n")
        print_help()

if __name__ == "__main__":
    main()
