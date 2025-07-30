# OVPN-Bulker

**OVPN-Bulker** is a terminal-based OpenVPN configuration manager for Linux using `nmcli`. Import, list, connect, disconnect, or delete all `.ovpn` profiles with a clean CLI experience and animated feedback.

## Usage

```bash
python main.py <directory> <username> <password>     # Import all .ovpn files
python main.py list                                  # Show imported VPNs
python main.py connect <vpn-name>                    # Connect to a VPN
python main.py disconnect <vpn-name>                 # Disconnect a VPN
python main.py delete-all                            # Delete all VPNs
python main.py help                                  # Show help