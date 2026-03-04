# 🔍 DNS Tunneling Simulation

> ⚠️ **For Educational Purposes Only** — This project demonstrates how DNS tunneling works in a safe, local environment. Do not use against systems you do not own or have explicit permission to test.

---

## What Is DNS Tunneling?

DNS tunneling is a technique that encodes non-DNS data inside DNS queries and responses. Because DNS traffic is rarely blocked by firewalls, attackers can use it to:

- Exfiltrate data from a compromised machine
- Maintain a covert command-and-control (C2) channel
- Bypass network security controls

This project simulates that entire flow **locally** so you can observe it safely.

---

## How It Works

```
[Client / "Victim"]                         [Server / "C2"]
       |                                           |
       |  1. Encode message as Base64              |
       |  2. Embed in DNS query subdomain          |
       |     e.g. aGVsbG8=.rnicrosft.com           |
       | ----------------------------------------> |
       |                                           |  3. Decode subdomain
       |                                           |  4. Look up response
       |  6. Decode TXT response                   |
       | <---------------------------------------- |
       |                                           |  5. Encode response as TXT record
```

All traffic looks like ordinary DNS queries to a network observer.

---

## Project Structure

```
.
├── dns_server.py   # Simulated C2 server — run this first
├── dns_client.py   # Simulated victim client
└── README.md
```

---

## Requirements

- Python 3.7+
- [`dnslib`](https://pypi.org/project/dnslib/)

```bash
pip install dnslib
```

---

## Usage

### 1. Start the Server

```bash
sudo python3 dns_server.py
```

The server listens on `127.0.0.1:5353` (UDP) and acts as a fake C2 server, decoding incoming DNS queries and replying via TXT records.

### 2. Run the Client

In a separate terminal:

```bash
python3 dns_client.py
```

You'll be prompted to enter a message to tunnel. Try one of the built-in commands:

| Command   | Server Response                        |
|-----------|----------------------------------------|
| `ping`    | `PONG - You reached the C2 server!`    |
| `hello`   | `Hello back from the attacker server!` |
| `whoami`  | `You are: victim-machine`              |
| `getkey`  | `SECRET_KEY_XYZ_9821`                  |

Or type any custom message — the server will acknowledge it.

Type `demo` to run an automated walkthrough of all built-in commands.

---

## Example Output

**Server terminal:**
```
[12:01:05] 📥 DNS Query received: aGVsbG8=.rnicrosft.com
[12:01:05] 🔓 Decoded message from client: 'hello'
[12:01:05] 📤 Sending back: 'Hello back from the attacker server!'
[12:01:05]    Encoded as TXT: 'SGVsbG8gYmFjay...'
```

**Client terminal:**
```
[12:01:05] 📤 Original message : 'hello'
[12:01:05]    Base64 encoded   : 'aGVsbG8='
[12:01:05]    DNS query sent   : 'aGVsbG8=.rnicrosft.com'
[12:01:05] 📥 Server responded : 'Hello back from the attacker server!'
```

---

## Encoding Scheme

- Messages are encoded with **Base64**
- `=` padding is replaced with `-` to be DNS-safe
- The encoded payload is prepended as a subdomain: `<payload>.rnicrosft.com`
- Responses are returned as **DNS TXT records**, also Base64-encoded

---

## Detection & Defense

This simulation is useful for understanding how to detect DNS tunneling in real environments:

- **Unusually long subdomains** — legitimate DNS queries rarely have long random-looking subdomains
- **High DNS query volume** to a single domain
- **TXT record responses** from non-standard resolvers
- **Entropy analysis** — Base64-encoded data has higher character entropy than normal hostnames
- Tools like Zeek, Suricata, or commercial NDR platforms can flag these patterns

---

## Disclaimer

This tool is strictly for **learning and research** in environments you own or control. DNS tunneling against production networks or systems without authorization is illegal and unethical.

---

