import sys
import os
import subprocess
from pathlib import Path

def print_help():
    print("""
[OVPN-BULKER] - Manage OpenVPN Profiles via NetworkManager

Usage:
  ovpn-bulker.py <command> [arguments]

Commands:
  install <dir> <username> <password>   Import all .ovpn files in the directory
  list                                  Show all imported VPNs
  delete-all                            Remove all imported VPNs
  connect <name>                        Connect to a specific VPN
  disconnect <name>                     Disconnect a VPN
  help                                  Show this message
""")

def get_all_vpn_names():
    result = subprocess.run(["nmcli", "-t", "-f", "NAME,TYPE", "connection", "show"], capture_output=True, text=True)
    return [line.split(":")[0] for line in result.stdout.strip().split("\n") if ":vpn" in line]

def import_vpn(file_path, username, password):
    name = os.path.splitext(os.path.basename(file_path))[0]
    subprocess.run(["nmcli", "connection", "import", "type", "openvpn", "file", file_path])
    subprocess.run(["nmcli", "connection", "modify", name, "vpn.user-name", username])
    subprocess.run(["nmcli", "connection", "modify", name, "+vpn.data", "password-flags=0"])
    subprocess.run(["nmcli", "connection", "modify", name, "vpn.secrets", f"password={password}"])
    return name

def delete_vpn(name):
    subprocess.run(["nmcli", "connection", "delete", name])

def delete_all_vpns():
    for name in get_all_vpn_names():
        delete_vpn(name)

def connect_vpn(name):
    subprocess.run(["nmcli", "connection", "up", name])

def disconnect_vpn(name):
    subprocess.run(["nmcli", "connection", "down", name])

def set_autoconnect(name, enabled=True):
    flag = "yes" if enabled else "no"
    subprocess.run(["nmcli", "connection", "modify", name, "connection.autoconnect", flag])

def install_all(directory, username, password):
    ovpn_files = list(Path(directory).glob("*.ovpn"))
    if not ovpn_files:
        print(f"[!] No .ovpn files found in {directory}")
        return

    print(f"[=] Installing {len(ovpn_files)} VPNs...\n")
    for file in ovpn_files:
        name = import_vpn(str(file), username, password)
        set_autoconnect(name, True)
        print(f" [+] Imported '{name}' and enabled autoconnect")
    print("\n[✓] All VPNs installed.\n")

def main():
    if len(sys.argv) < 2:
        print_help()
        return

    cmd = sys.argv[1].lower()

    if cmd == "install":
        if len(sys.argv) != 5:
            print("Usage: ovpn-bulker.py install <directory> <username> <password>")
            return
        _, _, directory, username, password = sys.argv
        install_all(directory, username, password)

    elif cmd == "list":
        names = get_all_vpn_names()
        print("\n[=] VPN Profiles:")
        for name in names:
            print(f"  - {name}")
        print()

    elif cmd == "delete-all":
        confirm = input("Are you sure you want to delete all VPNs? (y/N): ").lower()
        if confirm == "y":
            delete_all_vpns()
            print("[✓] All VPNs deleted.")
        else:
            print("Aborted.")

    elif cmd == "connect":
        if len(sys.argv) != 3:
            print("Usage: ovpn-bulker.py connect <vpn-name>")
            return
        connect_vpn(sys.argv[2])

    elif cmd == "disconnect":
        if len(sys.argv) != 3:
            print("Usage: ovpn-bulker.py disconnect <vpn-name>")
            return
        disconnect_vpn(sys.argv[2])

    elif cmd == "help":
        print_help()
    else:
        print(f"[!] Unknown command: {cmd}")
        print_help()

if __name__ == "__main__":
    main()
