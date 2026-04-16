#!/usr/bin/env python3
"""
main.py
Punto de entrada del gestor de proyectos MuleSoft.

Uso:
    python main.py <comando> [opciones]
    python -m mulesoft_manager <comando> [opciones]

Ejemplos:
    python main.py init
    python main.py client add
    python main.py client list
    python main.py tools check
"""

from mulesoft_manager.cli import cli

if __name__ == "__m