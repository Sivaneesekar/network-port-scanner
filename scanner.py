import socket
import threading
from datetime import datetime

# Service names for common ports
SERVICE_NAMES = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
    53: "DNS", 80: "HTTP", 110: "POP3", 135: "RPC",
    139: "NetBIOS", 143: "IMAP", 443: "HTTPS", 445: "SMB",
    3306: "MySQL", 3389: "RDP", 5900: "VNC", 8080: "HTTP-Alt"
}

target = input("Enter IP or hostname to scan: ")
print(f"\n{'='*50}")
print(f"  Scanning: {target}")
print(f"  Started : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*50}\n")

open_ports = []
lock = threading.Lock()

def scan_port(port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex((target, port))
        if result == 0:
            try:
                s.send(b'Hello\r\n')
                banner = s.recv(1024).decode().strip()
            except:
                banner = "No banner"
            service = SERVICE_NAMES.get(port, "Unknown")
            with lock:
                open_ports.append((port, service, banner))
                print(f"  [OPEN] Port {port:5d} | {service:10s} | {banner[:30]}")
        s.close()
    except:
        pass

# Scan ports 1-1024
threads = []
for port in range(1, 1025):
    t = threading.Thread(target=scan_port, args=(port,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

# HTML Report generate
report_name = f"scan_report_{target.replace('.', '_')}.html"
with open(report_name, "w", encoding="utf-8") as f:
    f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>Scan Report - {target}</title>
    <style>
        body {{ font-family: Arial; background: #1a1a2e; color: #eee; padding: 30px; }}
        h1 {{ color: #00d4ff; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th {{ background: #00d4ff; color: #000; padding: 10px; }}
        td {{ padding: 10px; border-bottom: 1px solid #333; }}
        tr:hover {{ background: #16213e; }}
        .open {{ color: #00ff88; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>🔍 Network Port Scan Report</h1>
    <p>Target: <b>{target}</b></p>
    <p>Scanned: <b>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</b></p>
    <p>Open Ports Found: <b>{len(open_ports)}</b></p>
    <table>
        <tr><th>Port</th><th>Service</th><th>Banner</th><th>Status</th></tr>
""")
    for port, service, banner in sorted(open_ports):
        f.write(f"""
        <tr>
            <td>{port}</td>
            <td>{service}</td>
            <td>{banner[:50]}</td>
            <td class="open">OPEN</td>
        </tr>""")
    f.write("""
    </table>
</body>
</html>""")

print(f"\n{'='*50}")
print(f"  Scan Complete! {len(open_ports)} open ports found.")
print(f"  HTML Report saved: {report_name}")
print(f"{'='*50}")
