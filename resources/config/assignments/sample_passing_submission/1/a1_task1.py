import socket
import os
import sys
from pathlib import Path
import json
sys.path.append(str(Path.cwd()))


def task_1() -> None:
    """
    This task retrieves system information and saves it to a file, `a1_task1.json`.
    
    The task will format the system information into a string in the following format:
    
    System Info:
    hostname - <hostname>
    ip_address - <ip_address>
    shell - <shell>
    user - <user>
    terminal - <terminal>
    
    Where:
    - <hostname> is the machine's hostname.
    - <ip_address> is the machine's IP address.
    - <shell> is the user's shell program (e.g., bash, zsh).
    - <user> is the current user's username.
    - <terminal> is the terminal program being used (e.g., vscode, bash).

    Example output:
    SYSTEM INFO:
    hostname - MICHA
    ip_address - 192.168.136.5
    shell - bash
    user - micha.vardy
    terminal - vscode
    
    The formatted information will be saved to a file called `a1_task1.json`.
    """

    # Retrieve system information
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    shell = Path(os.environ.get("SHELL")).stem
    user = os.environ.get('USERNAME')
    terminal = os.environ.get("TERM_PROGRAM")
    
    
    # TODO: fill in the info string with the following information and format it correctly:
    info = f"""
    SYSTEM INFO:
    hostname - {hostname}
    ip_address - {ip_address}
    shell - {shell}
    user - {user}
    terminal - {terminal}
    """

    # Write the information to a file
    Path("a1_task1.json").write_text(json.dumps({"system_info": info}), encoding="utf-8", errors="ignore")

if __name__ == "__main__":
    task_1()