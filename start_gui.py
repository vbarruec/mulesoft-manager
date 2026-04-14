#!/usr/bin/env python3
"""
start_gui.py
Lanzador de la interfaz gráfica web del MuleSoft Manager.

Inicia el servidor Flask en un puerto local y abre el navegador automáticamente.

Uso:
    python start_gui.py [--port 5000] [--no-browser] [--debug]
"""

from __future__ import annotations

import argparse
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

# Verificar dependencias antes de importar Flask
def _check_dependencies() -> bool:
    missing = []
    try:
        import flask
    except ImportError:
        missing.append("flask")
    try:
        import yaml
    except ImportError:
        missing.append("PyYAML")
    try:
        import click
    except ImportError:
        missing.append("click")
    try:
        import rich
    except ImportError:
        missing.append("rich")

    if missing:
        print("❌ Dependencias faltantes:")
        for pkg in missing:
            print(f"   pip install {pkg}")
        print("\nInstala todo con:")
        print("   pip install -r requirements.txt")
        print("   (o)  pip install -r requirements-gui.txt")
        return False
    return True


def _find_free_port(preferred: int = 5000) -> int:
    """Encuentra un puerto libre. Empieza por el preferido."""
    for port in range(preferred, preferred + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return preferred


def _wait_for_server(port: int, timeout: float = 10.0) -> bool:
    """Espera hasta que el servidor esté listo."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except (ConnectionRefusedError, OSError):
            time.sleep(0.2)
    return False


def _print_banner(port: int) -> None:
    """Imprime el banner de inicio."""
    url = f"http://127.0.0.1:{port}"
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║          ⚡  MuleSoft Manager — GUI Web              ║")
    print("╠══════════════════════════════════════════════════════╣")
    print(f"║  URL: {url:<46}║")
    print("║                                                      ║")
    print("║  Cierra esta ventana o presiona Ctrl+C para salir    ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="MuleSoft Manager — Interfaz gráfica web",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--port", type=int, default=5000,
                        help="Puerto para el servidor (default: 5000)")
    parser.add_argument("--no-browser", action="store_true",
                        help="No abrir el navegador automáticamente")
    parser.add_argument("--debug", action="store_true",
                        help="Modo debug Flask (recarga automática)")
    parser.add_argument("--host", default="127.0.0.1",
                        help="Host del servidor (default: 127.0.0.1)")
    args = parser.parse_args()

    # Verificar dependencias
    if not _check_dependencies():
        sys.exit(1)

    # Importar después de verificar dependencias
    from mulesoft_manager.gui.app import app

    port = _find_free_port(args.port)
    url = f"http://{args.host}:{port}"

    _print_banner(port)

    # Abrir navegador en un hilo separado (después de que el servidor arranque)
    if not args.no_browser:
        def open_browser():
            if _wait_for_server(port, timeout=15):
                webbrowser.open(url)
            else:
                print(f"⚠ No se pudo conectar al servidor. Abre manualmente: {url}")

        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()

    # Iniciar Flask
    try:
        app.run(
            host=args.host,
            port=port,
            debug=args.debug,
            use_reloader=args.debug,
            threaded=True,
        )
    except KeyboardInterrupt:
        print("\n\n👋 MuleSoft Manager GUI cerrado.")


if __name__ == "__main__":
    main()
