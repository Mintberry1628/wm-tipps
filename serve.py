# -*- coding: utf-8 -*-
"""Mini-Webserver fuer die WM-2026-Tipp-App.
Startet einen lokalen Server, der vom PC (localhost) UND vom Handy
(ueber WLAN / Tailscale, gleiche IP) erreichbar ist."""
import http.server, socketserver, socket, os, sys

PORT = int(os.environ.get("WM_PORT", "8026"))
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)

class H(http.server.SimpleHTTPRequestHandler):
    extensions_map = dict(http.server.SimpleHTTPRequestHandler.extensions_map)
    extensions_map.update({".webmanifest": "application/manifest+json",
                           ".js": "text/javascript", ".json": "application/json"})
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")  # immer frische Tipps
        super().end_headers()
    def log_message(self, *a):
        pass

def ips():
    out = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80)); out.append(s.getsockname()[0]); s.close()
    except Exception:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if ip not in out and not ip.startswith("127."):
                out.append(ip)
    except Exception:
        pass
    return out

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", PORT), H) as httpd:
        print("=" * 56)
        print("  WM 2026 KI-Tipps - Server laeuft")
        print("=" * 56)
        print("  Auf diesem PC:   http://localhost:%d" % PORT)
        for ip in ips():
            print("  Auf dem Handy:   http://%s:%d" % (ip, PORT))
        print("-" * 56)
        print("  (Handy: gleiches WLAN oder Tailscale. Beenden: Fenster")
        print("   schliessen oder Strg+C.)")
        print("=" * 56)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer beendet.")
