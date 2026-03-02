#!/usr/bin/env python3
"""
DNS Tunneling Simulation - SERVER SIDE
=======================================
Educational tool to demonstrate DNS tunneling concept.
Run this FIRST before the client.

Requirements: pip install dnslib
Usage: sudo python3 dns_server.py
"""

import base64
import socket
import threading
from datetime import datetime

try:
    from dnslib import DNSRecord, DNSHeader, DNSQuestion, RR, TXT, QTYPE, A
    from dnslib.server import DNSServer, BaseResolver, DNSLogger
except ImportError:
    print("[-] Missing dependency. Install it with:")
    print("    pip install dnslib")
    exit(1)

TUNNEL_DOMAIN = "tunnel.local"
SERVER_IP = "127.0.0.1"
SERVER_PORT = 5353

# Simulated secret responses from the C2 server
C2_RESPONSES = {
    "ping": "PONG - You reached the C2 server!",
    "hello": "Hello back from the attacker server!",
    "whoami": "You are: victim-machine",
    "getkey": "SECRET_KEY_XYZ_9821",
}

received_messages = []

def log(msg, color="\033[0m"):
    reset = "\033[0m"
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{color}[{timestamp}] {msg}{reset}")

class TunnelResolver(BaseResolver):
    def resolve(self, request, handler):
        qname = str(request.q.qname).rstrip(".")
        reply = request.reply()

        log(f"📥 DNS Query received: {qname}", "\033[93m")  # Yellow

        # Check if query is for our tunnel domain
        if TUNNEL_DOMAIN in qname:
            subdomain = qname.replace(f".{TUNNEL_DOMAIN}", "").replace(TUNNEL_DOMAIN, "")

            if subdomain:
                try:
                    # Decode the base64 encoded message from subdomain
                    # Replace - with = for valid base64 padding
                    padded = subdomain.replace("-", "=")
                    decoded = base64.b64decode(padded).decode("utf-8")
                    received_messages.append(decoded)

                    log(f"🔓 Decoded message from client: '{decoded}'", "\033[92m")  # Green

                    # Craft a response
                    response_text = C2_RESPONSES.get(decoded.lower(), f"ACK: received '{decoded}'")
                    encoded_response = base64.b64encode(response_text.encode()).decode()

                    log(f"📤 Sending back: '{response_text}'", "\033[96m")  # Cyan
                    log(f"   Encoded as TXT: '{encoded_response}'", "\033[90m")  # Gray

                    # Send response as TXT record (this is the tunnel response)
                    reply.add_answer(RR(qname, QTYPE.TXT, rdata=TXT(encoded_response), ttl=1))

                except Exception as e:
                    log(f"⚠️  Could not decode: {subdomain} | Error: {e}", "\033[91m")
                    reply.add_answer(RR(qname, QTYPE.TXT, rdata=TXT("ERROR"), ttl=1))
            else:
                # Base domain query — just acknowledge
                reply.add_answer(RR(qname, QTYPE.A, rdata=A(SERVER_IP), ttl=1))
        else:
            log(f"   (Not a tunnel query, ignoring)", "\033[90m")

        return reply


def print_banner():
    print("\033[91m")  # Red
    print("=" * 60)
    print("   DNS TUNNELING SIMULATION - SERVER (C2)")
    print("   For Educational Purposes Only")
    print("=" * 60)
    print("\033[0m")
    print(f"  Listening on : {SERVER_IP}:{SERVER_PORT} (UDP)")
    print(f"  Tunnel domain: *.{TUNNEL_DOMAIN}")
    print(f"  Encoding     : Base64 in DNS subdomains")
    print(f"  Response type: TXT records")
    print()
    print("  How it works:")
    print("  1. Client encodes a message in base64")
    print("  2. Sends it as a DNS query subdomain")
    print("  3. Server decodes it and responds via TXT record")
    print("  4. All of this looks like 'normal' DNS traffic!")
    print()
    print("  Waiting for tunnel connections...\n")


if __name__ == "__main__":
    print_banner()

    resolver = TunnelResolver()

    # Custom logger to suppress default dnslib output
    class QuietLogger(DNSLogger):
        def log_request(self, *args): pass
        def log_reply(self, *args): pass
        def log_truncated(self, *args): pass
        def log_error(self, *args): pass
        def log_data(self, *args): pass

    server = DNSServer(resolver, port=SERVER_PORT, address=SERVER_IP, logger=QuietLogger())

    try:
        server.start_thread()
        log(f"✅ DNS Tunnel Server running on port {SERVER_PORT}", "\033[92m")
        log("   Press Ctrl+C to stop\n", "\033[90m")

        while True:
            threading.Event().wait(1)

    except KeyboardInterrupt:
        print("\n")
        log("🛑 Server stopped.", "\033[91m")
        if received_messages:
            print("\n📋 Messages received during session:")
            for i, msg in enumerate(received_messages, 1):
                print(f"   {i}. {msg}")
        server.stop()
