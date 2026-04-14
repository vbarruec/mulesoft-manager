"""
vscode.py
Gestión de configuración VS Code y archivos .code-workspace por cliente.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from rich.console import Console

from .config import ClientConfig, GlobalConfig
from .constants import VSCODE_WORKSPACE_SETTINGS, VSCODE_EXTENSIONS, MULE_REGIONS

console = Console()


# ---------------------------------------------------------------------------
# Workspace file (.code-workspace)
# ---------------------------------------------------------------------------

def create_workspace_file(root: Path, client: ClientConfig, global_cfg: GlobalConfig) -> Path:
    """
    Crea el archivo .code-workspace de VS Code para el cliente.
    Incluye configuración de Java, Maven y Git específica del cliente.
    """
    ws_dir = root / ".vscode-workspaces"
    ws_dir.mkdir(parents=True, exist_ok=True)
    ws_path = client.workspace_file_path

    # Carpetas del workspace (todos los repos del cliente)
    folders = [{"path": str(client.project_dir).replace("\\", "/")}]
    # También añadir cada repo individualmente si ya existen
    if client.project_dir.exists():
        for repo_dir in sorted(client.project_dir.iterdir()):
            if repo_dir.is_dir() and (repo_dir / ".git").exists():
                rel = os.path.relpath(repo_dir, ws_dir).replace("\\", "/")
                folders.append({"path": rel, "name": repo_dir.name})

    # Settings específicos del cliente
    settings = _build_client_settings(root, client, global_cfg)

    workspace_data = {
        "folders": folders,
        "settings": settings,
        "extensions": {
            "recommendations": global_cfg.extensions or VSCODE_EXTENSIONS
        },
    }

    ws_path.write_text(
        json.dumps(workspace_data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    console.print(f"[green]Workspace VS Code creado: {ws_path}[/green]")
    return ws_path


def update_workspace_file(root: Path, client: ClientConfig, global_cfg: GlobalConfig) -> Path:
    """
    Actualiza el .code-workspace del cliente (p.ej. después de añadir repos).
    """
    return create_workspace_file(root, client, global_cfg)


def open_workspace(client: ClientConfig) -> None:
    """Abre el workspace del cliente en VS Code."""
    ws_path = client.workspace_file_path
    if not ws_path.exists():
        console.print(f"[red]Workspace no encontrado: {ws_path}[/red]")
        return

    code_cmd = _find_vscode_cmd()
    if code_cmd is None:
        console.print(f"[yellow]VS Code no encontrado. Abre manualmente: {ws_path}[/yellow]")
        return

    try:
        subprocess.Popen([code_cmd, str(ws_path)])
        console.print(f"[green]Abriendo VS Code con el workspace de {client.display_name}...[/green]")
    except Exception as e:
        console.print(f"[red]Error abriendo VS Code: {e}[/red]")


# ---------------------------------------------------------------------------
# Settings del workspace
# ---------------------------------------------------------------------------

def _build_client_settings(
    root: Path,
    client: ClientConfig,
    global_cfg: GlobalConfig
) -> dict:
    """
    Construye el dict de settings VS Code para el cliente.
    Incluye rutas de Java, Maven y configuración MuleSoft.
    """
    settings = dict(VSCODE_WORKSPACE_SETTINGS)  # base

    # Java
    java_home = global_cfg.java_home
    if java_home and java_home.exists():
        settings["java.jdt.ls.java.home"] = str(java_home).replace("\\", "/")
        settings["java.home"] = str(java_home).replace("\\", "/")

    # Maven
    maven_home = global_cfg.maven_home
    if maven_home and maven_home.exists():
        mvn_path = maven_home / "bin" / "mvn.cmd"
        settings["java.configuration.maven.userSettings"] = str(
            client.maven_settings_path
        ).replace("\\", "/")
        if mvn_path.exists():
            settings["maven.executable.path"] = str(mvn_path).replace("\\", "/")
        settings["maven.settingsFile"] = str(client.maven_settings_path).replace("\\", "/")

    # Git config del cliente
    settings["git.path"] = (shutil.which("git") or "git").replace("\\", "/")

    # Anypoint Platform region
    region_info = MULE_REGIONS.get(client.mule_region, MULE_REGIONS["us"])
    settings["mulesoft.anypointUrl"] = region_info["anypoint_url"]

    # Mostrar nombre del cliente en la barra de estado
    settings["window.title"] = f"[{client.display_name}] ${{activeEditorShort}}${{separator}}${{rootName}}"

    # Terminal: establecer GIT_CONFIG_GLOBAL al del cliente
    gitconfig_path = str(client.gitconfig_path).replace("\\", "/")
    settings["terminal.integrated.env.windows"] = {
        "GIT_CONFIG_GLOBAL": gitconfig_path,
        "MULESOFT_CLIENT": client.name,
        "MULESOFT_REGION": client.mule_region,
    }

    # Workspace trust
    settings["security.workspace.trust.untrustedFiles"] = "open"

    return settings


# ---------------------------------------------------------------------------
# Extensions
# ---------------------------------------------------------------------------

def install_extensions(extensions: list[str]) -> None:
    """Instala las extensiones recomendadas en VS Code."""
    code_cmd = _find_vscode_cmd()
    if code_cmd is None:
        console.print("[red]VS Code no encontrado. Instala VS Code primero.[/red]")
        return

    already_installed = _get_installed_extensions(code_cmd)
    to_install = [e for e in extensions if e.lower() not in [x.lower() for x in already_installed]]

    if not to_install:
        console.print("[green]Todas las extensiones ya están instaladas.[/green]")
        return

    console.print(f"[bold]Instalando {len(to_install)} extensión(es)...[/bold]")
    failed = []

    for ext in to_install:
        console.print(f"  [cyan]→ {ext}[/cyan]", end="", flush=True)
        try:
            result = subprocess.run(
                [code_cmd, "--install-extension", ext, "--force"],
                capture_output=True, text=True, timeout=120
            )
            if result.returncode == 0:
                console.print(" [green]✓[/green]")
            else:
                console.print(f" [red]✗[/red]")
                failed.append(ext)
        except Exception as e:
            console.print(f" [red]✗ ({e})[/red]")
            failed.append(ext)

    if failed:
        console.print(f"\n[yellow]No instaladas ({len(failed)}):[/yellow]")
        for f in failed:
            console.print(f"  • {f}")
    else:
        console.print("\n[green]✅ Todas las extensiones instaladas.[/green]")


def _get_installed_extensions(code_cmd: str) -> list[str]:
    """Obtiene la lista de extensiones instaladas."""
    try:
        result = subprocess.run(
            [code_cmd, "--list-extensions"],
            capture_output=True, text=True, timeout=30
        )
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except Exception:
        return []


def _find_vscode_cmd() -> Optional[str]:
    """Busca el ejecutable de VS Code."""
    cmd = shutil.which("code")
    if cmd:
        return cmd
    candidates = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Microsoft VS Code" / "bin" / "code.cmd",
        Path("C:/Program Files/Microsoft VS Code/bin/code.cmd"),
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return None


# ---------------------------------------------------------------------------
# Maven settings.xml
# ---------------------------------------------------------------------------

def create_maven_settings(root: Path, client: ClientConfig) -> Path:
    """
    Crea el archivo settings.xml de Maven para el cliente.
    """
    from .constants import MAVEN_SETTINGS_TEMPLATE, MULE_REGIONS

    maven_dir = root / ".maven" / client.name
    maven_dir.mkdir(parents=True, exist_ok=True)
    settings_path = maven_dir / "settings.xml"

    region_info = MULE_REGIONS.get(client.mule_region, MULE_REGIONS["us"])

    content = MAVEN_SETTINGS_TEMPLATE.format(
        anypoint_username=client.anypoint_username or "TU_USUARIO_ANYPOINT",
        anypoint_password=client.anypoint_password or "TU_PASSWORD_ANYPOINT",
        nexus_url=region_info["nexus_url"],
    )

    settings_path.write_text(content, encoding="utf-8")
    console.print(f"[green]Maven settings.xml creado: {settings_path}[/green]")

    if not client.anypoint_username:
        console.print(f"[yellow]⚠ Edita las credenciales de Anypoint en: {settings_path}[/yellow]")

    return settings_path
